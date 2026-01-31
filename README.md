# 🤖 AI Training Assistant

An intelligent, secure AI assistant for employee onboarding that provides instant, accurate answers using advanced RAG technology. Features conversation memory, persistent chat history, and enterprise-grade security.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991.svg)](https://openai.com/)

## ✨ Key Features

### 🔐 **Secure Authentication**
- User registration with email validation
- Encrypted password storage with bcrypt
- Persistent session management
- Secure logout and session timeout

### 💬 **Smart Conversations**
- **Persistent Chat History**: Never lose your conversations - all chats saved to database
- **Conversation Memory**: AI remembers your previous questions and answers for natural dialogue
- **Multi-turn Conversations**: Seamlessly discuss topics across multiple messages
- **Context Awareness**: Uses up to 10 recent messages to understand your questions better

### 🎯 **Intelligent Routing**
Automatically categorizes your questions into 4 specialized areas:
- 📚 **General Company Info** - Values, culture, structure
- 👔 **Role-Specific Guidance** - Job responsibilities, tools, processes
- 📋 **Policies & Admin** - HR policies, IT access, expense reports
- 💬 **Direct Chat** - General questions and friendly conversation

### 📚 **Advanced Knowledge Retrieval**
- Searches across company documents, policies, and role guides
- Provides source citations for every answer
- Semantic search using AI embeddings
- Fast responses (typically under 2 seconds)

### 🛡️ **Enterprise-Grade Security**
- Personal information detection (SSN, credit cards, emails)
- Harmful content filtering
- Rate limiting (10 requests/minute per user)
- Prompt injection protection
- Input sanitization and validation

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 2GB free disk space

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ai-training-assistant
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-openai-api-key-here
```

5. **Load training data**
```bash
python src/retrieval/vector_store.py
```
This will process your company documents and create the knowledge base (takes ~2-5 minutes).

6. **Launch the application**
```bash
streamlit run ui/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

### First Time Setup
1. Click **"Register"** tab on the login page
2. Create your account with username and password
3. Accept the terms of use
4. Switch to **"Login"** tab and sign in

### Using the Assistant
1. **Ask Questions**: Type your question in the chat input
2. **View Answers**: AI responds with relevant information and source citations
3. **Continue Conversation**: Ask follow-up questions - the AI remembers your context
4. **Switch Topics**: Click **"New Chat"** to start a fresh conversation
5. **Review History**: Access previous conversations from the sidebar

### Example Questions
- "What are our company values?"
- "What does a Product Manager do here?"
- "How do I submit expense reports?"
- "What tools does a Data Analyst use?"
- "How many PTO days do I get?"

## 🏗️ Architecture Overview
```
User Question
     ↓
Input Validation & Safety Check
     ↓
Query Router (Conversation-Aware)
     ↓
[Company Info | Role Guide | Policy Docs | Direct Chat]
     ↓
Vector Database Search (ChromaDB)
     ↓
LLM with Context + Retrieved Documents
     ↓
Output Safety Check
     ↓
Answer + Source Citations
     ↓
Save to Chat History
```

**Technology Stack:**
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Database**: ChromaDB
- **Framework**: LangChain
- **UI**: Streamlit
- **Database**: SQLite3
- **Auth**: bcrypt password hashing

## 📊 Performance

| Metric | Target |
|--------|--------|
| Routing Accuracy | 95%+ |
| Citation Rate | 98%+ |
| Response Time | <2 seconds |
| Vector Search | <500ms |
| Concurrent Users | 10+ |

## 🔧 Configuration

Edit `config.yaml` to customize:
```yaml
llm:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 1000

retrieval:
  top_k: 3                    # Number of documents to retrieve
  similarity_threshold: 0.7   # Minimum relevance score

guardrails:
  enable_content_check: true
  rate_limit_requests: 10     # Per minute per user
```

## 📁 Project Structure
```
ai-training-assistant/
├── src/
│   ├── agents/          # AI assistant & routing logic
│   ├── database/        # User auth & chat history
│   ├── retrieval/       # Vector database & search
│   ├── guardrails/      # Content safety
│   └── prompts/         # LLM templates
├── ui/
│   └── app.py          # Streamlit web interface
├── data/
│   └── corpus/         # Company documents
├── config.yaml         # Configuration
└── requirements.txt    # Dependencies
```

## 🛡️ Security Features

- ✅ Personal information detection and blocking
- ✅ Harmful content prevention
- ✅ Rate limiting per user
- ✅ Input sanitization
- ✅ Prompt injection protection
- ✅ Session security
- ✅ Password encryption (bcrypt)

### Deploy to Streamlit Cloud

**Streamlit Cloud** is the easiest way to deploy your app with zero infrastructure management.

#### Step 1: Push Code to GitHub

```bash
# Initialize git and commit your code
git init
git add .
git commit -m "Initial commit: AI Training Assistant"

# Add GitHub remote and push
git remote add origin https://github.com/your-username/ai-training-assistant.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account
4. Select repository: `ai-training-assistant`
5. Set main file path to: `ui/app.py`
6. Click **"Deploy"**

#### Step 3: Add Secrets in Streamlit Cloud

1. In your app's dashboard, click **⚙️ Settings**
2. Go to **Secrets** tab
3. Paste your OpenAI API key:
```
OPENAI_API_KEY = "your-openai-api-key-here"
```
4. Click **Save** (app will auto-redeploy)

#### Step 4: Update After Changes

Every time you make changes, just push to GitHub:

```bash
# Make your changes
git add .
git commit -m "Feature: Description of changes"
git push origin main
```

**Streamlit Cloud automatically redeploys your app within 1-2 minutes!**

---

## 📈 Evaluation

Run automated tests to assess performance:
```bash
python src/evaluation/evaluator.py
```

Evaluates:
- Routing accuracy
- Retrieval quality
- Citation accuracy
- Response coherence
- Safety compliance

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - see LICENSE file for details

## 📚 Technical Documentation

For detailed technical documentation, architecture details, and developer guides, see [docs/README.md](docs/README.md)

## 💡 Support

If you encounter any issues:
1. Check the [Technical Documentation](docs/README.md)
2. Review the configuration in `config.yaml`
3. Ensure your OpenAI API key is valid
4. Check logs in `logs/` directory

---

**Built with ❤️ using OpenAI, LangChain, ChromaDB, and Streamlit**