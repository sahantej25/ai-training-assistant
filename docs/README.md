# AI Training Assistant - Technical Documentation

## Architecture Overview
```
User Question
     ↓
Query Router (GPT-4o-mini)
     ↓
[general_company | role_specific | admin_policy | direct_llm]
     ↓
ChromaDB Retrieval (if needed)
     ↓
Context + Question → GPT-4o-mini
     ↓
Answer with Citations
```

## Components

### 1. Vector Store (`src/retrieval/vector_store.py`)
- Loads corpus documents into ChromaDB
- Creates separate collections per route
- Handles similarity search

### 2. Query Router (`src/agents/router.py`)
- Classifies questions into 4 routes
- Uses GPT-4o-mini for classification
- Returns routing decision

### 3. AI Assistant (`src/agents/assistant.py`)
- Orchestrates entire pipeline
- Handles RAG and direct LLM responses
- Returns structured results

### 4. Streamlit UI (`ui/app.py`)
- Chat interface
- Real-time interaction
- Shows routing and sources

### 5. Evaluator (`src/evaluation/evaluator.py`)
- Tests routing accuracy
- Measures citation quality
- Generates metrics

## Routes

1. **general_company**: Company info, values, culture
2. **role_specific**: Job roles and responsibilities
3. **admin_policy**: HR policies, admin processes
4. **direct_llm**: Out-of-scope, no retrieval needed

## Metrics

- **Routing Accuracy**: % of questions routed correctly
- **Citation Rate**: % of answers that include sources
- **Relevance Rate**: % of answers that are substantive

## Future Enhancements

- [ ] Add confidence scores to routing
- [ ] Implement feedback mechanism
- [ ] Add conversation memory
- [ ] Support file uploads
- [ ] Multi-language support