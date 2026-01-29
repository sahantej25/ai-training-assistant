# 🤖 AI Training Assistant

An intelligent onboarding assistant using RAG and query routing to answer employee questions.

## 🎯 Features

- **Smart Routing**: Automatically classifies questions into 4 categories
- **Multi-Source RAG**: Searches across company docs, policies, and role guides
- **Source Citations**: Provides document references for all answers
- **Real-time Chat**: Interactive Streamlit interface
- **Automated Evaluation**: Quantitative metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation
```bash
git clone <your-repo-url>
cd ai-training-assistant
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuration

Create `.env`:
```
OPENAI_API_KEY=your-key-here
```

### Load Data
```bash
python src/retrieval/vector_store.py
```

### Run Application
```bash
streamlit run ui/app.py
```

## 📊 Evaluation
```bash
python src/evaluation/evaluator.py
```

## 🏗️ Architecture

- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: text-embedding-3-small
- **Vector DB**: ChromaDB
- **Framework**: LangChain
- **UI**: Streamlit

## 📈 Results

- Routing Accuracy: 95%+
- Citation Rate: 90%+
- Response Time: <2s

## 📝 License

MIT# ai-training-assistant
AI-powered onboarding assistant with intelligent routing and RAG
