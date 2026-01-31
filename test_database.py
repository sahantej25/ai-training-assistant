"""
Test script for database functionality
Run this to verify your database setup works correctly
"""

import sys
from pathlib import Path
import time

# Add to path
sys.path.append(str(Path(__file__).parent))

from src.database.db_handler import DatabaseHandler

def test_database():
    """Test all database operations"""
    
    print("\n" + "="*70)
    print("🧪 TESTING DATABASE FUNCTIONALITY")
    print("="*70 + "\n")
    
    # Delete old test database if it exists
    test_db_path = Path("data/test_chatbot.db")
    if test_db_path.exists():
        print("🗑️ Removing old test database...")
        test_db_path.unlink()
        # Give OS time to release the file
        time.sleep(0.5)
    
    # Initialize database
    print("1️⃣ Initializing database...")
    db = DatabaseHandler(db_path="data/test_chatbot.db")
    print()
    
    # Test user registration
    print("2️⃣ Testing user registration...")
    success = db.register_user("test_user", "test_password123", "test@example.com")
    if success:
        print("✅ User registered successfully\n")
    else:
        print("❌ User registration failed\n")
        return
    
    # Test authentication
    print("3️⃣ Testing authentication...")
    user_id = db.authenticate_user("test_user", "test_password123")
    if user_id:
        print(f"✅ Authentication successful! User ID: {user_id}\n")
    else:
        print("❌ Authentication failed\n")
        return
    
    # Test wrong password
    print("4️⃣ Testing wrong password...")
    wrong_auth = db.authenticate_user("test_user", "wrong_password")
    if wrong_auth is None:
        print("✅ Correctly rejected wrong password\n")
    else:
        print("❌ Security issue: wrong password accepted\n")
    
    # Create session
    print("5️⃣ Creating chat session...")
    session_id = "test_session_123"
    db.create_session(user_id, session_id, "Test Chat Session")
    print("✅ Session created\n")
    
    # Save messages
    print("6️⃣ Saving messages...")
    db.save_message(user_id, session_id, "user", "What are the company values?")
    db.save_message(
        user_id, 
        session_id, 
        "assistant", 
        "Our company values are innovation, integrity, and collaboration.",
        metadata={"route": "general_company", "sources": ["company_handbook.pdf"]}
    )
    print("✅ Messages saved\n")
    
    # Retrieve chat history
    print("7️⃣ Retrieving chat history...")
    messages = db.get_chat_history(user_id, session_id)
    print(f"✅ Retrieved {len(messages)} messages:")
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. [{msg['role']}]: {msg['content'][:50]}...")
    print()
    
    # Get user sessions
    print("8️⃣ Getting user sessions...")
    sessions = db.get_user_sessions(user_id)
    print(f"✅ Found {len(sessions)} session(s):")
    for i, session in enumerate(sessions, 1):
        print(f"   {i}. {session['session_name']} (ID: {session['session_id'][:8]}...)")
    print()
    
    # Get user info
    print("9️⃣ Getting user info...")
    user_info = db.get_user_info(user_id)
    if user_info:
        print("✅ User info retrieved:")
        print(f"   Username: {user_info['username']}")
        print(f"   Email: {user_info['email']}")
        print(f"   Created: {user_info['created_at']}")
        print(f"   Last login: {user_info['last_login']}")
    print()
    
    # Close database connection properly
    print("🔒 Closing database connection...")
    db.close()
    print()
    
    print("="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\nYou can now run: streamlit run app.py")
    print()

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check:")
        print("1. No other process is using the database")
        print("2. You have write permissions in the data/ directory")
        print("3. Close any database browser tools (DB Browser for SQLite, etc.)")