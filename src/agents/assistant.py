from openai import OpenAI
import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import config
from src.agents.router import QueryRouter
from src.retrieval.vector_store import VectorStore
from src.prompts.templates import (
    RAG_SYSTEM_PROMPT, 
    RAG_USER_TEMPLATE, 
    DIRECT_LLM_PROMPT
)


class AITrainingAssistant:
    """Complete AI Training Assistant with routing and RAG"""
    
    def __init__(self):
        print("🤖 Initializing AI Training Assistant...")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.router = QueryRouter()
        self.vector_store = VectorStore()
        
        print("✅ Assistant ready!\n")
    
    def answer(self, question: str) -> Dict:
        """
        Answer a user question with intelligent routing
        
        Args:
            question: User's question
            
        Returns:
            Dict with answer, route, sources, and metadata
        """
        # Step 1: Route the question
        routing_info = self.router.classify_with_confidence(question)
        route = routing_info['route']
        
        print(f"🎯 Routed to: {route}")
        
        # Step 2: Handle based on route
        if route == "direct_llm":
            # No retrieval needed - direct LLM response
            return self._direct_answer(question, route)
        else:
            # Retrieval-based answer
            return self._rag_answer(question, route)
    
    def _rag_answer(self, question: str, route: str) -> Dict:
        """Generate answer using RAG"""
        
        # Retrieve relevant documents
        print(f"📚 Retrieving from {route} collection...")
        docs = self.vector_store.query(question, route, k=config.TOP_K)
        
        if not docs:
            return {
                "question": question,
                "answer": "I couldn't find relevant information in the knowledge base for this question.",
                "route": route,
                "sources": [],
                "context_used": False
            }
        
        # Prepare context
        context_parts = []
        sources = []
        
        for i, doc in enumerate(docs, 1):
            source_file = doc.metadata.get('source_file', 'unknown')
            context_parts.append(f"[{source_file}]\n{doc.page_content}\n")
            sources.append(source_file)
        
        context = "\n---\n".join(context_parts)
        
        print(f"✅ Retrieved {len(docs)} documents")
        
        # Generate answer
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": RAG_USER_TEMPLATE.format(
                        context=context,
                        question=question
                    )}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "question": question,
                "answer": answer,
                "route": route,
                "sources": list(set(sources)),  # Unique sources
                "context_used": True,
                "num_chunks": len(docs)
            }
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                "question": question,
                "answer": "I encountered an error generating the answer. Please try again.",
                "route": route,
                "sources": [],
                "context_used": False,
                "error": str(e)
            }
    
    def _direct_answer(self, question: str, route: str) -> Dict:
        """Handle direct LLM responses (no retrieval)"""
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": DIRECT_LLM_PROMPT.format(question=question)}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "question": question,
                "answer": answer,
                "route": route,
                "sources": [],
                "context_used": False
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                "question": question,
                "answer": "I encountered an error. Please try again.",
                "route": route,
                "sources": [],
                "context_used": False,
                "error": str(e)
            }


def test_assistant():
    """Test the complete assistant"""
    print("\n" + "="*70)
    print("🤖 TESTING AI TRAINING ASSISTANT")
    print("="*70 + "\n")
    
    assistant = AITrainingAssistant()
    
    test_questions = [
        "What are our company's core values?",
        "What does a Product Manager do here?",
        "How do I submit an expense claim?",
        "What's the weather like today?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*70}")
        print(f"Question {i}: {question}")
        print('='*70)
        
        result = assistant.answer(question)
        
        print(f"\n📍 Route: {result['route']}")
        print(f"📚 Sources: {result['sources']}")
        print(f"\n💬 Answer:\n{result['answer']}\n")


if __name__ == "__main__":
    test_assistant()