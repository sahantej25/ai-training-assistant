# src/retrieval/vector_store.py
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from pathlib import Path
import json
from typing import List
import os
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import config


class VectorStore:
    def __init__(self):
        print("🚀 Initializing Vector Store...")
        
        # Validate config
        config.validate()
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Create persist directory
        os.makedirs(config.CHROMA_DIR, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        
        # Load manifest
        with open(config.MANIFEST_PATH, 'r') as f:
            self.manifest = json.load(f)
        
        self.collections = {}
        print(f"✅ Vector Store initialized\n")
    
    def load_corpus(self):
        """Load all documents from corpus"""
        print("="*70)
        print("📚 LOADING CORPUS INTO CHROMADB")
        print("="*70 + "\n")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        routes = self.manifest['routes']
        total_chunks = 0
        
        for route_name, route_info in routes.items():
            if route_name == "direct_llm":
                continue
            
            print(f"📂 Route: {route_name}")
            all_docs = []
            
            for path_str in route_info['suggested_paths']:
                # FIX: Convert relative path to absolute using DATA_DIR
                if not path_str.startswith(('/', 'C:', 'D:')):  # Relative path
                    # Remove 'corpus/' prefix if exists and reconstruct
                    clean_path = path_str.replace('corpus/', '')
                    path = config.CORPUS_DIR / clean_path
                else:
                    path = Path(path_str)
                
                if not path.exists():
                    print(f"   ⚠️  Path not found: {path}")
                    continue
                
                print(f"   📖 Loading: {path}")
                
                try:
                    loader = DirectoryLoader(
                        str(path),
                        glob="*.md",
                        loader_cls=TextLoader,
                        loader_kwargs={'autodetect_encoding': True}
                    )
                    docs = loader.load()
                    
                    # Add metadata
                    for doc in docs:
                        doc.metadata['route'] = route_name
                        doc.metadata['source_file'] = Path(doc.metadata.get('source', '')).name
                    
                    all_docs.extend(docs)
                    print(f"      ✅ {len(docs)} documents")
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            
            if not all_docs:
                print(f"   ⚠️  No documents for {route_name}\n")
                continue
            
            # Split into chunks
            chunks = text_splitter.split_documents(all_docs)
            print(f"   ✂️  Created {len(chunks)} chunks")
            total_chunks += len(chunks)
            
            # Create collection
            collection_name = f"{route_name}_docs"
            
            try:
                self.client.delete_collection(collection_name)
            except:
                pass
            
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=str(config.CHROMA_DIR)
            )
            
            self.collections[route_name] = vectorstore
            print(f"   ✅ Collection created\n")
        
        print("="*70)
        print(f"✅ LOADED {total_chunks} TOTAL CHUNKS ACROSS {len(self.collections)} COLLECTIONS")
        print("="*70 + "\n")
    
    def query(self, query_text: str, route: str, k: int = None) -> List:
        """Query a specific route"""
        k = k or config.TOP_K
        
        if route not in self.collections:
            collection_name = f"{route}_docs"
            try:
                self.collections[route] = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(config.CHROMA_DIR)
                )
            except Exception as e:
                print(f"❌ Error loading collection: {e}")
                return []
        
        try:
            results = self.collections[route].similarity_search(query_text, k=k)
            return results
        except Exception as e:
            print(f"❌ Query error: {e}")
            return []
    
    def test_retrieval(self):
        """Test retrieval with sample queries"""
        print("="*70)
        print("🧪 TESTING RETRIEVAL")
        print("="*70 + "\n")
        
        tests = [
            ("What are our company values?", "general_company"),
            ("What does a Product Manager do?", "role_specific"),
            ("How do I submit expenses?", "admin_policy")
        ]
        
        for query, route in tests:
            print(f"❓ Query: {query}")
            print(f"🎯 Route: {route}")
            
            results = self.query(query, route, k=2)
            
            if results:
                print(f"✅ Found {len(results)} results")
                for i, doc in enumerate(results, 1):
                    source = doc.metadata.get('source_file', 'unknown')
                    preview = doc.page_content[:120].replace('\n', ' ')
                    print(f"   [{i}] {source}: {preview}...")
            else:
                print("❌ No results")
            print()


def main():
    """Main execution"""
    print("\n" + "🤖 AI TRAINING ASSISTANT - DATA LOADER\n")
    
    # Initialize and load
    vs = VectorStore()
    vs.load_corpus()
    
    # Test retrieval
    vs.test_retrieval()
    
    print("="*70)
    print("✅ DATA LOADING COMPLETE - READY FOR NEXT STEP!")
    print("="*70)


if __name__ == "__main__":
    main()