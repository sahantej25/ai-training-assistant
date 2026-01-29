# src/agents/router.py

from openai import OpenAI
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import config
from src.prompts.templates import ROUTER_SYSTEM_PROMPT, ROUTER_USER_TEMPLATE


class QueryRouter:
    """Routes user queries to appropriate knowledge sources"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.valid_routes = ["general_company", "role_specific", "admin_policy", "direct_llm"]
    
    def classify(self, question: str) -> str:
        """
        Classify a question into one of the routes
        
        Args:
            question: User's question
            
        Returns:
            Route name (general_company, role_specific, admin_policy, or direct_llm)
        """
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": ROUTER_USER_TEMPLATE.format(question=question)}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            route = response.choices[0].message.content.strip().lower()
            
            # Validate route
            if route in self.valid_routes:
                return route
            else:
                # Default to direct_llm if classification is unclear
                print(f"⚠️ Unknown route '{route}', defaulting to direct_llm")
                return "direct_llm"
                
        except Exception as e:
            print(f"❌ Router error: {e}")
            return "direct_llm"
    
    def classify_with_confidence(self, question: str) -> dict:
        """Classify and return confidence info"""
        route = self.classify(question)
        return {
            "route": route,
            "question": question,
            "is_retrieval_needed": route != "direct_llm"
        }


def test_router():
    """Test the router with sample queries"""
    print("\n🧪 TESTING QUERY ROUTER\n")
    
    router = QueryRouter()
    
    test_queries = [
        "What are our company values?",
        "What does a Product Manager do?",
        "How do I submit expenses?",
        "What's the weather today?",
        "Can you approve my leave request?",
        "What tools does a Data Analyst use?",
        "How many PTO days do I get?",
        "Tell me a joke"
    ]
    
    for query in test_queries:
        result = router.classify_with_confidence(query)
        route = result['route']
        needs_retrieval = "✅ RAG" if result['is_retrieval_needed'] else "❌ Direct"
        
        print(f"❓ {query}")
        print(f"   🎯 Route: {route} ({needs_retrieval})")
        print()


if __name__ == "__main__":
    test_router()