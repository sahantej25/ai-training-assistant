import sqlite3
import hashlib
import json
from datetime import datetime
import time
from pathlib import Path
from typing import Optional, Dict, List

class DatabaseHandler:
    def __init__(self, db_path: str = "data/chatbot.db"):
        """Initialize database handler.

        This handler opens short-lived connections per operation to reduce
        contention and avoids holding a long-lived connection across threads.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure DB initialized and tables created
        self.create_tables()
        print("✅ Database initialized successfully")

    def _get_conn(self):
        """Create a new sqlite3 connection for each operation."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Use a short-lived connection for DDL
        for attempt in range(5):
            try:
                with self._get_conn() as conn:
                    cursor = conn.cursor()
                    # Users table
                    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)

                    # Sessions table
                    cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                session_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

                    # Messages table
                    cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
                    conn.commit()
                break
            except sqlite3.OperationalError as e:
                if 'locked' in str(e).lower() and attempt < 4:
                    time.sleep(0.2 * (2 ** attempt))
                    continue
                else:
                    print(f"❌ create_tables error: {e}")
                    break
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register a new user"""
        try:
            password_hash = self._hash_password(password)

            # If email is empty, generate a unique placeholder to avoid UNIQUE constraint collisions
            if not email or str(email).strip() == "":
                placeholder = f"__no_email__{username}_{int(datetime.utcnow().timestamp())}@local"
                email = placeholder

            for attempt in range(5):
                try:
                    with self._get_conn() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                            (username, password_hash, email)
                        )
                        conn.commit()
                    return True
                except sqlite3.OperationalError as e:
                    if 'locked' in str(e).lower() and attempt < 4:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise
            return False
            
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                print(f"❌ Username '{username}' already exists")
            elif "email" in str(e).lower():
                print(f"❌ Email '{email}' already registered")
            return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user_id if successful"""
        try:
            password_hash = self._hash_password(password)
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id FROM users WHERE username = ? AND password_hash = ?",
                    (username, password_hash)
                )
                result = cursor.fetchone()

                if result:
                    user_id = result['user_id']
                    # Update last login
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
                        (user_id,)
                    )
                    conn.commit()
                    return user_id

            return None
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    def create_session(self, user_id: int, session_id: str, session_name: str):
        """Create a new chat session"""
        try:
            for attempt in range(5):
                try:
                    with self._get_conn() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT OR REPLACE INTO sessions (session_id, user_id, session_name) VALUES (?, ?, ?)",
                            (session_id, user_id, session_name)
                        )
                        conn.commit()
                    break
                except sqlite3.OperationalError as e:
                    if 'locked' in str(e).lower() and attempt < 4:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise
        except Exception as e:
            print(f"❌ Session creation error: {e}")
    
    def save_message(
        self, 
        user_id: int, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Save a chat message"""
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            for attempt in range(5):
                try:
                    with self._get_conn() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            """INSERT INTO messages (user_id, session_id, role, content, metadata) 
                               VALUES (?, ?, ?, ?, ?)""",
                            (user_id, session_id, role, content, metadata_json)
                        )

                        # Update session last activity
                        cursor.execute(
                            "UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?",
                            (session_id,)
                        )
                        conn.commit()
                    break
                except sqlite3.OperationalError as e:
                    if 'locked' in str(e).lower() and attempt < 4:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise
        except Exception as e:
            print(f"❌ Message save error: {e}")
    
    def get_chat_history(self, user_id: int, session_id: str) -> List[Dict]:
        """Retrieve chat history for a session"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT role, content, metadata, timestamp 
                       FROM messages 
                       WHERE user_id = ? AND session_id = ? 
                       ORDER BY timestamp ASC""",
                    (user_id, session_id)
                )

                messages = []
                for row in cursor.fetchall():
                    message = {
                        'role': row['role'],
                        'content': row['content'],
                        'timestamp': row['timestamp']
                    }
                    if row['metadata']:
                        message['metadata'] = json.loads(row['metadata'])
                    messages.append(message)
                return messages
            
        except Exception as e:
            print(f"❌ Chat history error: {e}")
            return []
    
    def get_user_sessions(self, user_id: int) -> List[Dict]:
        """Get all sessions for a user"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT session_id, session_name, created_at, last_activity 
                       FROM sessions 
                       WHERE user_id = ? 
                       ORDER BY last_activity DESC""",
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"❌ Sessions retrieval error: {e}")
            return []
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT username, email, created_at, last_login FROM users WHERE user_id = ?",
                    (user_id,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
            
        except Exception as e:
            print(f"❌ User info error: {e}")
            return None
    
    def delete_session(self, user_id: int, session_id: str):
        """Delete a chat session and its messages"""
        try:
            for attempt in range(5):
                try:
                    with self._get_conn() as conn:
                        cursor = conn.cursor()
                        # Delete messages first (foreign key constraint)
                        cursor.execute(
                            "DELETE FROM messages WHERE user_id = ? AND session_id = ?",
                            (user_id, session_id)
                        )

                        # Delete session
                        cursor.execute(
                            "DELETE FROM sessions WHERE user_id = ? AND session_id = ?",
                            (user_id, session_id)
                        )
                        conn.commit()
                    break
                except sqlite3.OperationalError as e:
                    if 'locked' in str(e).lower() and attempt < 4:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise
        except Exception as e:
            print(f"❌ Session deletion error: {e}")
    
    def close(self):
        """Close database connection"""
        # No persistent connection to close when using per-call connections.
        print("✅ Database handler cleanup (no persistent connection to close)")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()