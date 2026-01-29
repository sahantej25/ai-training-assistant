import streamlit as st
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.assistant import AITrainingAssistant
from src.utils.config import config

# Page config
st.set_page_config(
    page_title="AI Training Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .route-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .route-company { background-color: #d4edda; color: #155724; }
    .route-role { background-color: #cce5ff; color: #004085; }
    .route-policy { background-color: #fff3cd; color: #856404; }
    .route-direct { background-color: #f8d7da; color: #721c24; }
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        background-color: #e9ecef;
        color: #495057;
        font-size: 0.75rem;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize assistant
@st.cache_resource
def load_assistant():
    """Load assistant once and cache it"""
    with st.spinner("🚀 Initializing AI Training Assistant..."):
        return AITrainingAssistant()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "assistant" not in st.session_state:
    st.session_state.assistant = load_assistant()

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Training Assistant")
    st.markdown("---")
    
    st.markdown("#### 📊 System Info")
    st.info(f"""
    **Model:** {config.OPENAI_MODEL}
    **Embeddings:** {config.EMBEDDING_MODEL}
    **Top-K Results:** {config.TOP_K}
    """)
    
    st.markdown("#### 🎯 Routing Categories")
    st.markdown("""
    <div class="route-badge route-company">📚 Company Info</div>
    <div class="route-badge route-role">👔 Role Guides</div>
    <div class="route-badge route-policy">📋 Policies & Admin</div>
    <div class="route-badge route-direct">💬 General Chat</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 💡 Example Questions")
    example_questions = [
        "What are our company values?",
        "What does a Product Manager do?",
        "How do I submit expenses?",
        "What tools does a Data Analyst use?",
        "How do I request PTO?",
    ]
    
    for question in example_questions:
        if st.button(question, key=question, use_container_width=True):
            st.session_state.selected_question = question
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### 📈 Stats")
    st.metric("Total Questions", len([m for m in st.session_state.messages if m["role"] == "user"]))

# Main header
st.markdown('<div class="main-header">🤖 AI Training Assistant</div>', unsafe_allow_html=True)
st.markdown("##### Welcome! Ask me anything about company policies, roles, or onboarding.")
st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show metadata for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            
            # Route badge
            route = metadata.get("route", "unknown")
            route_class = {
                "general_company": "route-company",
                "role_specific": "route-role",
                "admin_policy": "route-policy",
                "direct_llm": "route-direct"
            }.get(route, "route-direct")
            
            st.markdown(f'<span class="route-badge {route_class}">Route: {route}</span>', unsafe_allow_html=True)
            
            # Sources
            if metadata.get("sources"):
                st.markdown("**📚 Sources:**")
                for source in metadata["sources"]:
                    st.markdown(f'<span class="source-badge">{source}</span>', unsafe_allow_html=True)

# Handle example question selection
if "selected_question" in st.session_state:
    user_input = st.session_state.selected_question
    del st.session_state.selected_question
else:
    user_input = st.chat_input("Ask me anything about the company...")

# Process user input
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            result = st.session_state.assistant.answer(user_input)
        
        # Display answer
        st.markdown(result["answer"])
        
        # Display metadata
        route = result["route"]
        route_class = {
            "general_company": "route-company",
            "role_specific": "route-role",
            "admin_policy": "route-policy",
            "direct_llm": "route-direct"
        }.get(route, "route-direct")
        
        st.markdown(f'<span class="route-badge {route_class}">Route: {route}</span>', unsafe_allow_html=True)
        
        # Sources
        if result.get("sources"):
            st.markdown("**📚 Sources:**")
            for source in result["sources"]:
                st.markdown(f'<span class="source-badge">{source}</span>', unsafe_allow_html=True)
    
    # Add assistant message to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "metadata": {
            "route": result["route"],
            "sources": result.get("sources", [])
        }
    })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.875rem;'>
    🤖 AI Training Assistant | Powered by OpenAI GPT-4o-mini | Built with Streamlit
</div>
""", unsafe_allow_html=True)