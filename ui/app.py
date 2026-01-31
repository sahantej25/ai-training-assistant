import streamlit as st
import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.assistant import AITrainingAssistant
from src.utils.config import config
from src.database.db_handler import DatabaseHandler

# Page config
st.set_page_config(
    page_title="AI Training Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with all improvements
st.markdown("""
<style>
    /* ========== TYPOGRAPHY & LAYOUT ========== */
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        opacity: 0.75;
        margin-bottom: 2rem;
    }
    
    /* ========== LOGIN/REGISTER CONTAINER ========== */
    .login-container {
        max-width: 480px;
        margin: 2rem auto;
        padding: 2.5rem;
        border-radius: 16px;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    @media (prefers-color-scheme: dark) {
        .login-container {
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }
    }
    
    /* ========== INPUT FIELDS ========== */
    .stTextInput > div > div > input {
        height: 54px !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        padding: 0 16px !important;
    }
    
    /* Chat input - Purple focus instead of red */
    .stChatInput > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ========== BUTTONS - IMPROVED HOVER EFFECTS ========== */
    /* Primary buttons - Purple gradient */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        height: 50px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c8df0 0%, #8a5db4 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.45) !important;
    }
    
    /* Secondary buttons - Better hover */
    .stButton > button[kind="secondary"] {
        background-color: rgba(108, 117, 125, 0.08) !important;
        border: 1.5px solid rgba(108, 117, 125, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: rgba(108, 117, 125, 0.15) !important;
        border-color: rgba(108, 117, 125, 0.4) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Tab hover effects */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.08) !important;
    }
    
    /* ========== ROUTE BADGES (Original Design) ========== */
    .route-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .route-company { 
        background-color: #d4edda; 
        color: #155724; 
    }
    
    .route-role { 
        background-color: #cce5ff; 
        color: #004085; 
    }
    
    .route-policy { 
        background-color: #fff3cd; 
        color: #856404; 
    }
    
    .route-direct { 
        background-color: #f8d7da; 
        color: #721c24; 
    }
    
    .route-blocked { 
        background-color: #f8d7da; 
        color: #721c24; 
        border: 2px solid #dc3545;
        font-weight: 700;
        animation: pulse-warning 2s ease-in-out infinite;
    }
    
    @keyframes pulse-warning {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* ========== SOURCE BADGES ========== */
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        background-color: #e9ecef;
        color: #495057;
        font-size: 0.75rem;
        margin: 0.25rem;
    }
    
    /* ========== INFO BOXES ========== */
    .info-box-small {
        padding: 0.75rem 1.25rem;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        font-size: 0.9rem;
        text-align: center;
        margin: 1.25rem 0;
        font-weight: 500;
    }
    
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* ========== SUCCESS BOX ========== */
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    /* ========== HIDE LOADING SPINNER TEXT ========== */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent !important;
    }
    
    /* ========== METRICS ========== */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* ========== FORMS ========== */
    .stForm {
        border: 1px solid rgba(0, 0, 0, 0.1);
        padding: 1.8rem;
        border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.02);
    }
    
    @media (prefers-color-scheme: dark) {
        .stForm {
            border-color: rgba(255, 255, 255, 0.12);
        }
    }
    
    /* ========== FOOTER ========== */
    .footer {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        font-size: 0.85rem;
        opacity: 0.6;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    @media (prefers-color-scheme: dark) {
        .footer {
            border-top-color: rgba(255, 255, 255, 0.1);
        }
    }
    
    /* ========== DIVIDERS ========== */
    hr {
        margin: 1.5rem 0;
        opacity: 0.15;
    }
    
    /* ========== SIDEBAR STYLING ========== */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.02);
    }
    
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.02);
        }
    }
    
    /* ========== CUSTOM SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Simple module-level caches to avoid Streamlit's "Running <fn>" UI during first-run
_db_cache = None
_assistant_cache = None

def load_database():
    """Load database handler once and cache it in-module."""
    global _db_cache
    if _db_cache is None:
        _db_cache = DatabaseHandler()
    return _db_cache


def load_assistant():
    """Load assistant once and cache it in-module. Suppresses stdout/stderr."""
    global _assistant_cache
    if _assistant_cache is None:
        import io
        import contextlib

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            _assistant_cache = AITrainingAssistant()

    return _assistant_cache

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db" not in st.session_state:
    st.session_state.db = load_database()
if "assistant" not in st.session_state:
    st.session_state.assistant = None
if "show_guardrails_info" not in st.session_state:
    st.session_state.show_guardrails_info = False

def login_page():
    """Display login/register page"""
    
    # Main header with gradient
    st.markdown('<div class="main-header">🤖 AI Training Assistant</div>', unsafe_allow_html=True)
    
    # Subtitle
    st.markdown('<p class="subtitle">🛡️ Secure AI Assistant with Content Safety Protection</p>', unsafe_allow_html=True)
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Safety info (collapsible)
        with st.expander("🛡️ About Safety Features", expanded=False):
            st.markdown("""
            <div class="info-box">
            <strong>Content Safety Guardrails Include:</strong><br><br>
            ✅ Personal information detection & blocking<br>
            ✅ Harmful content prevention<br>
            ✅ Rate limiting (10 requests/minute)<br>
            ✅ Input sanitization & validation<br>
            ✅ Prompt injection protection<br>
            ✅ Professional tone enforcement
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login/Register tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### Welcome Back")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if submit:
                    if username and password:
                        user_id = st.session_state.db.authenticate_user(username, password)
                        
                        if user_id:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user_id
                            st.session_state.username = username
                            # CRITICAL: Load assistant and ensure it's set
                            with st.spinner("Loading AI Assistant..."):
                                st.session_state.assistant = load_assistant()
                            st.success(f"✅ Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("⚠️ Please enter both username and password")
        
        with tab2:
            with st.form("register_form", clear_on_submit=False):
                st.markdown("### Create New Account")
                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
                new_email = st.text_input("Email (optional)", placeholder="your@email.com", key="reg_email")
                new_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
                
                st.markdown("<br>", unsafe_allow_html=True)
                accept_terms = st.checkbox("I agree to use this assistant responsibly and follow content policies")
                
                st.markdown("<br>", unsafe_allow_html=True)
                register = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if register:
                    if not accept_terms:
                        st.error("❌ Please accept the terms to register")
                    elif new_username and new_password:
                        if new_password == confirm_password:
                            if len(new_password) < 6:
                                st.error("❌ Password must be at least 6 characters")
                            elif st.session_state.db.register_user(new_username, new_password, new_email):
                                st.markdown("""
                                <div class="success-box">
                                ✅ <strong>Registration successful!</strong> Please switch to the Login tab.
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.error("❌ Username already exists or email already registered")
                        else:
                            st.error("❌ Passwords do not match")
                    else:
                        st.warning("⚠️ Please fill in all required fields")

def create_new_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    session_name = "New Chat"
    
    st.session_state.db.create_session(
        st.session_state.user_id,
        session_id,
        session_name
    )
    
    st.session_state.current_session_id = session_id
    st.session_state.messages = []

def update_session_name(session_id: str, first_question: str):
    """Update session name with the first question"""
    try:
        import sqlite3
        conn = sqlite3.connect("data/chatbot.db")
        cursor = conn.cursor()
        
        # Truncate question for clean display
        if len(first_question) > 50:
            session_name = first_question[:50] + "..."
        else:
            session_name = first_question
        
        cursor.execute(
            "UPDATE sessions SET session_name = ? WHERE session_id = ?",
            (session_name, session_id)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating session name: {e}")

def load_session(session_id: str):
    """Load a previous chat session"""
    st.session_state.current_session_id = session_id
    
    # Load messages from database
    messages = st.session_state.db.get_chat_history(
        st.session_state.user_id,
        session_id
    )
    
    st.session_state.messages = messages

def chat_page():
    """Main chat interface"""
    
    # CRITICAL: Ensure assistant is loaded
    if st.session_state.assistant is None:
        with st.spinner("🚀 Initializing AI Assistant..."):
            st.session_state.assistant = load_assistant()
    
    # Handle example question selection
    user_input = None
    if "selected_question" in st.session_state:
        user_input = st.session_state.selected_question
        del st.session_state.selected_question
    
    # Sidebar
    with st.sidebar:
        # Friendly greeting
        st.markdown(f"### 👋 Hello, {st.session_state.username}!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.current_session_id = None
                st.session_state.messages = []
                st.session_state.assistant = None
                st.rerun()
        
        with col2:
            if st.button("🛡️ Safety", use_container_width=True, type="secondary"):
                st.session_state.show_guardrails_info = not st.session_state.show_guardrails_info
        
        st.markdown("---")
        
        # Safety info (collapsible)
        if st.session_state.show_guardrails_info:
            st.markdown("### 🛡️ Safety Features")
            st.markdown("""
            <div class="info-box">
            <strong>Active Protection:</strong><br>
            ✅ Personal info detection<br>
            ✅ Harmful content blocking<br>
            ✅ Rate limiting (10/min)<br>
            ✅ Input validation<br>
            ✅ Prompt injection protection
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
        
        # Chat History
        st.markdown("### 💬 Chat History")
        
        # New Chat button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            create_new_session()
            st.rerun()
        
        # Display previous sessions
        sessions = st.session_state.db.get_user_sessions(st.session_state.user_id)
        
        if sessions:
            st.markdown("#### Recent Conversations")
            for session in sessions[:10]:
                is_current = session["session_id"] == st.session_state.current_session_id
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    if st.button(
                        session["session_name"],
                        key=f"session_{session['session_id']}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary"
                    ):
                        load_session(session["session_id"])
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session['session_id']}", type="secondary"):
                        st.session_state.db.delete_session(
                            st.session_state.user_id,
                            session["session_id"]
                        )
                        if is_current:
                            create_new_session()
                        st.rerun()
        
        st.markdown("---")
        
        # System Info with Guardrails
        st.markdown("#### 📊 System Info")
        st.info(f"""
**Model:** {config.OPENAI_MODEL}  
**Embeddings:** {config.EMBEDDING_MODEL}  
**Guardrails:** ✅ Active (Content Safety)
        """)
        
        # Routing Categories
        st.markdown("#### 🎯 Routing Categories")
        st.markdown("""
        <div class="route-badge route-company">📚 Company Info</div>
        <div class="route-badge route-role">👔 Role Guides</div>
        <div class="route-badge route-policy">📋 Policies & Admin</div>
        <div class="route-badge route-direct">💬 General Chat</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Example Questions
        st.markdown("#### 💡 Example Questions")
        example_questions = [
            "What are our company values?",
            "What does a Product Manager do?",
            "How do I submit expenses?",
            "What tools does a Data Analyst use?",
            "How do I request PTO?",
        ]
        
        for question in example_questions:
            if st.button(question, key=question, use_container_width=True, type="secondary"):
                st.session_state.selected_question = question
                st.rerun()
        
        st.markdown("---")
        
        # Session Stats
        st.markdown("#### 📈 Stats")
        total_questions = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Total Questions", total_questions)
    
    # Main content area
    st.markdown('<div class="main-header">🤖 AI Training Assistant</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ask me anything about company policies, roles, or onboarding</p>', unsafe_allow_html=True)
    
    # Small safety notice with better styling
    st.markdown("""
    <div class="info-box-small">
    🛡️ Protected by Content Safety Guardrails - All inputs validated for safe interactions
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create session if needed
    if not st.session_state.current_session_id:
        create_new_session()
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                route = metadata.get("route", "unknown")
                
                # Show blocked route with guardrails badge
                if route == "guardrail_blocked":
                    st.markdown('<span class="route-badge route-blocked">🚫 Blocked by Guardrails</span>', 
                              unsafe_allow_html=True)
                    if metadata.get("reason"):
                        st.caption(f"Reason: {metadata['reason']}")
                else:
                    route_class = {
                        "general_company": "route-company",
                        "role_specific": "route-role",
                        "admin_policy": "route-policy",
                        "direct_llm": "route-direct"
                    }.get(route, "route-direct")
                    
                    st.markdown(f'<span class="route-badge {route_class}">Route: {route}</span>', 
                              unsafe_allow_html=True)
                
                # Sources
                if metadata.get("sources"):
                    st.markdown("**📚 Sources:**")
                    sources_html = " ".join(
                        [f'<span class="source-badge">{source}</span>' for source in metadata["sources"]]
                    )
                    st.markdown(sources_html, unsafe_allow_html=True)
    
    # Chat input
    if not user_input:
        user_input = st.chat_input("Ask me anything about the company...")
    
    # Process input with guardrails
    if user_input:
        is_first_message = len(st.session_state.messages) == 0
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.db.save_message(
            st.session_state.user_id,
            st.session_state.current_session_id,
            "user",
            user_input
        )
        
        # Update session name with first question
        if is_first_message:
            update_session_name(st.session_state.current_session_id, user_input)
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get response with guardrails validation
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                # CRITICAL: Check assistant exists before calling
                if st.session_state.assistant is None:
                    st.session_state.assistant = load_assistant()
                conversation_history = []
                for msg in st.session_state.messages:
                    conversation_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                # Call assistant with user_id for rate limiting and guardrails
                result = st.session_state.assistant.answer(
                    user_input, 
                    user_id=st.session_state.user_id
                )
            
            st.markdown(result["answer"])
            
            # Display metadata with guardrails info
            route = result["route"]
            
            if result.get("blocked"):
                st.markdown('<span class="route-badge route-blocked">🚫 Blocked by Guardrails</span>', 
                          unsafe_allow_html=True)
                if result.get("reason"):
                    st.caption(f"Reason: {result['reason']}")
            else:
                route_class = {
                    "general_company": "route-company",
                    "role_specific": "route-role",
                    "admin_policy": "route-policy",
                    "direct_llm": "route-direct"
                }.get(route, "route-direct")
                
                st.markdown(f'<span class="route-badge {route_class}">Route: {route}</span>', 
                          unsafe_allow_html=True)
            
            if result.get("sources"):
                st.markdown("**📚 Sources:**")
                sources_html = " ".join(
                    [f'<span class="source-badge">{source}</span>' for source in result["sources"]]
                )
                st.markdown(sources_html, unsafe_allow_html=True)
        
        # Save response
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "metadata": {
                "route": result["route"],
                "sources": result.get("sources", []),
                "blocked": result.get("blocked", False),
                "reason": result.get("reason", "")
            }
        })
        
        st.session_state.db.save_message(
            st.session_state.user_id,
            st.session_state.current_session_id,
            "assistant",
            result["answer"],
            metadata={
                "route": result["route"],
                "sources": result.get("sources", []),
                "blocked": result.get("blocked", False),
                "reason": result.get("reason", "")
            }
        )
        
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
    🤖 AI Training Assistant | 🛡️ Content Safety Protected | Powered by OpenAI GPT-4o-mini | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)

# Main app
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()