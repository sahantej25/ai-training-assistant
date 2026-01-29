# src/utils/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Paths - FIXED
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    CORPUS_DIR = DATA_DIR / "corpus"
    CHROMA_DIR = BASE_DIR / "chroma_db"
    
    # Evaluation
    EVAL_SET_PATH = DATA_DIR / "evaluation_set.csv"
    MANIFEST_PATH = DATA_DIR / "dataset_manifest.json"
    
    # Retrieval settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K = 3
    
    # Routes
    ROUTES = ["general_company", "role_specific", "admin_policy", "direct_llm"]
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY not found in .env")
        if not cls.CORPUS_DIR.exists():
            raise ValueError(f"❌ Corpus directory not found: {cls.CORPUS_DIR}")
        
        # Check if corpus has content
        corpus_folders = list(cls.CORPUS_DIR.iterdir())
        if not corpus_folders:
            raise ValueError(f"❌ Corpus directory is empty: {cls.CORPUS_DIR}")
        
        print("✅ Configuration validated")
        print(f"   Corpus path: {cls.CORPUS_DIR}")
        print(f"   Found folders: {[f.name for f in corpus_folders if f.is_dir()]}")
        return True

config = Config()