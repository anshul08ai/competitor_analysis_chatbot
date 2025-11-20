import streamlit as st
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import requests
import os,sys
from pathlib import Path


utils_path = Path.cwd().parent / "src" / "graph"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from workflow import compiled

# st.session_state.source_urls= []
# st.session_state.source_urls= []

if "source_urls" not in st.session_state:
    st.session_state.source_urls = []

# Page configuration
st.set_page_config(
    page_title="Chat Application",
    page_icon="💬",
    layout="wide"
)

with st.sidebar:
    st.header("Sources")
    for url in st.session_state.source_urls:
        st.markdown(f"[{url}]({url})")

# ==================== AZURE OPENAI CONFIGURATION ====================

# Azure OpenAI credentials - UPDATED

# ==================== CACHING FUNCTIONS ====================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_chat_history(session_id: str) -> List[Dict]:
    """
    Simulates API call to fetch chat history.
    In production, replace with actual API endpoint.
    """
    time.sleep(0.5)  # Simulate API delay
    
    # Mock data - replace with actual API call
    mock_sessions = {
        "session_1": [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "session_2": [
            {"role": "user", "content": "What's the weather?"},
            {"role": "assistant", "content": "I can't check real-time weather, but I can help with other questions!"}
        ]
    }
    
    return mock_sessions.get(session_id, [])

@st.cache_data(ttl=60, show_spinner=False)  # Cache for 1 minute, hide spinner for cache
def send_message_to_azure_openai(message: str, chat_history: List[Dict]) -> str:
    response=compiled.invoke({'query':message})
    # st.session_state.source_urls = response.get('analyser_output',{}).get('best_url',[])
    st.session_state.source_urls = response.get('web_urls',[])[:3]
    output = response['output']
    return output

# ==================== SESSION STATE INITIALIZATION ====================

def initialize_session_state():
    """Initialize all session state variables if they don't exist."""
    
    # Navigation state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # User authentication state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_guest' not in st.session_state:
        st.session_state.is_guest = False
    
    # User database (simulated - in production, use a real database)
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {
            'demo': 'password123'  # Default demo user
        }
    
    # Chat state - Enhanced for dynamic persistence
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = []
    if 'chat_sessions' not in st.session_state:
        # Store multiple chat sessions with their histories
        # Format: {session_id: {'name': str, 'timestamp': str, 'messages': List[Dict]}}
        st.session_state.chat_sessions = {}
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    # Bookmarks - Enhanced storage structure
    if 'bookmarks' not in st.session_state:
        # Store bookmarks with message content, role, timestamp, and session reference
        # Format: [{'content': str, 'role': str, 'timestamp': str, 'session_id': str}]
        st.session_state.bookmarks = []
    
    # Input key for clearing text input
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0

# ==================== NAVIGATION FUNCTIONS ====================

def navigate_to(page: str):
    """Navigate to a specific page by updating session state."""
    st.session_state.page = page
    st.rerun()

def logout():
    """Log out the user and return to home page. Saves current session before logout."""
    # Save current chat session before logging out (preserve chat history)
    if st.session_state.current_chat and len(st.session_state.current_chat) > 0:
        save_current_session()
    
    # Clear user authentication state
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_guest = False
    
    # Reset current chat view (but keep saved sessions)
    st.session_state.current_chat = []
    st.session_state.current_session_id = None
    
    navigate_to('home')

# ==================== PAGE 1: HOME PAGE ====================

def home_page():
    """Main landing page with Guest and Login options."""
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("💬 Welcome to AI Assistant")
        st.markdown("---")
        st.markdown("### Get started by choosing an option below:")
        st.markdown("")
        
        # Guest button
        if st.button("🌐 Continue as Guest", use_container_width=True, type="primary"):
            st.session_state.is_guest = True
            st.session_state.logged_in = True
            st.session_state.username = "Guest"
            navigate_to('chat')
        
        st.markdown("")
        
        # Login button
        if st.button("🔐 Login", use_container_width=True):
            navigate_to('login')
        
        st.markdown("---")
        st.markdown("*Guest mode provides limited features. Login for full access.*")

# ==================== PAGE 2: LOGIN PAGE ====================

def login_page():
    """Login and registration page."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Login")
        st.markdown("---")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                login_button = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            with col_b:
                register_button = st.form_submit_button("Register", use_container_width=True)
        
        # Handle login
        if login_button:
            if username and password:
                # Check credentials
                if username in st.session_state.users_db and st.session_state.users_db[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.is_guest = False
                    st.success(f"Welcome back, {username}!")
                    time.sleep(1)
                    navigate_to('chat')
                else:
                    st.error("Invalid username or password!")
            else:
                st.warning("Please enter both username and password.")
        
        # Handle registration
        if register_button:
            if username and password:
                # Check if user already exists
                if username in st.session_state.users_db:
                    st.error("Username already exists! Please choose a different username.")
                else:
                    # Register new user
                    st.session_state.users_db[username] = password
                    st.success(f"Account created successfully for {username}! You can now login.")
            else:
                st.warning("Please enter both username and password to register.")
        
        st.markdown("---")
        
        # Back to home button
        if st.button("← Back to Home", use_container_width=True):
            navigate_to('home')
        
        # Show demo credentials
        with st.expander("Demo Credentials"):
            st.info("Username: demo\nPassword: password123")

def save_current_session():
    """
    Save current chat session to session_state for persistence.
    Creates or updates a session with current chat history.
    """
    if st.session_state.current_chat and len(st.session_state.current_chat) > 0:
        # Generate session ID if new chat
        if not st.session_state.current_session_id:
            timestamp = datetime.now()
            session_id = f"session_{int(timestamp.timestamp())}"
            st.session_state.current_session_id = session_id
        
        # Extract first user message as session name (truncate if too long)
        session_name = "New Chat"
        for msg in st.session_state.current_chat:
            if msg["role"] == "user":
                session_name = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break
        
        # Save session with full message history
        st.session_state.chat_sessions[st.session_state.current_session_id] = {
            'name': session_name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'messages': st.session_state.current_chat.copy()  # Store full chat history
        }

def load_chat_session(session_id: str):
    """
    Load a previously saved chat session.
    Restores the full chat history from session_state.
    """
    if session_id in st.session_state.chat_sessions:
        st.session_state.current_session_id = session_id
        # Restore complete message history
        st.session_state.current_chat = st.session_state.chat_sessions[session_id]['messages'].copy()
    else:
        st.warning(f"Session {session_id} not found!")

def add_bookmark(message: Dict, session_id: Optional[str] = None):
    """
    Add a message to bookmarks with metadata.
    
    Args:
        message: The message dict with 'role' and 'content'
        session_id: Optional session identifier for reference
    """
    bookmark = {
        'content': message['content'],
        'role': message['role'],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'session_id': session_id or st.session_state.current_session_id
    }
    
    # Check if already bookmarked (avoid duplicates)
    is_duplicate = any(
        b['content'] == bookmark['content'] and 
        b['role'] == bookmark['role'] 
        for b in st.session_state.bookmarks
    )
    
    if not is_duplicate:
        st.session_state.bookmarks.append(bookmark)
        return True
    return False

# ==================== PAGE 3: CHAT INTERFACE ====================

def chat_page():
    """Main chat interface with sidebar and chat area."""
    
    # Sidebar for chat sessions and bookmarks
    with st.sidebar:
        st.title("💬 Chat Sessions")
        
        # Display current user
        if st.session_state.is_guest:
            st.info("👤 Logged in as: **Guest**")
        else:
            st.success(f"👤 Logged in as: **{st.session_state.username}**")
        
        st.markdown("---")
        
        # New chat button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            # Save current session before starting new chat
            save_current_session()
            
            # Reset for new chat
            st.session_state.current_chat = []
            st.session_state.current_session_id = None
            st.rerun()
        
        st.markdown("### Previous Chats")
        
        # Display previous chat sessions (sorted by timestamp, newest first)
        sorted_sessions = sorted(
            st.session_state.chat_sessions.items(),
            key=lambda x: x[1]['timestamp'],
            reverse=True
        )
        
        if sorted_sessions:
            for session_id, session_info in sorted_sessions:
                # Create button for each saved session
                button_label = f"📄 {session_info['name']}\n*{session_info['timestamp']}*"
                
                if st.button(
                    button_label,
                    key=f"session_{session_id}",
                    use_container_width=True
                ):
                    # Save current chat before switching
                    save_current_session()
                    
                    # Load selected session with full history
                    load_chat_session(session_id)
                    st.rerun()
        else:
            st.info("No previous chats yet. Start a conversation!")
        
        st.markdown("---")
        
        # Bookmarks section - Enhanced display
        st.markdown("### 🔖 Bookmarks")
        if st.session_state.bookmarks:
            for idx, bookmark in enumerate(st.session_state.bookmarks):
                with st.expander(f"🔖 {bookmark['role'].title()} - {bookmark['timestamp']}"):
                    st.markdown(f"**Content:** {bookmark['content']}")
                    if bookmark.get('session_id'):
                        st.caption(f"From session: {bookmark['session_id']}")
                    
                    # Remove bookmark button
                    if st.button("🗑️ Remove", key=f"remove_bookmark_{idx}"):
                        st.session_state.bookmarks.pop(idx)
                        st.success("Bookmark removed!")
                        time.sleep(0.3)
                        st.rerun()
        else:
            st.info("No bookmarks yet. Click 🔖 next to any message to bookmark it!")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Main chat area
    st.title("💬 Chat Interface")
    
    # Display current session info
    if st.session_state.current_session_id:
        session_info = st.session_state.chat_sessions[st.session_state.current_session_id]
        st.caption(f"📄 {session_info['name']} - {session_info['timestamp']}")
    else:
        st.caption("📝 New Chat")
    
    st.markdown("---")
    
    # Chat display area - Enhanced with dynamic rendering
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.current_chat:
            # Render all messages in chat history
            for idx, message in enumerate(st.session_state.current_chat):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    # Add bookmark button for each message
                    col1, col2, col3 = st.columns([6, 1, 1])
                    with col2:
                        # Unique key for each bookmark button based on message index
                        if st.button("🔖", key=f"bookmark_{idx}_{message['role']}"):
                            # Add message to bookmarks
                            if add_bookmark(message):
                                st.success("✅ Bookmarked!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.info("Already bookmarked!")
                                time.sleep(0.5)
        else:
            st.info("👋 Start a conversation by typing a message below!")
    
    st.markdown("---")
    
    # Chat input area
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message...",
            key=f"user_input_{st.session_state.input_key}",
            label_visibility="collapsed",
            placeholder="Type your message here..."
        )
    
    with col2:
        send_button = st.button("Send ➤", use_container_width=True, type="primary")
    
    # Handle sending message - Enhanced with Azure OpenAI integration
    if send_button and user_input:
        # Add user message to current chat history
        user_message = {
            "role": "user",
            "content": user_input
        }
        st.session_state.current_chat.append(user_message)
        
        # Show a spinner while waiting for API response
        with st.spinner("🤔 Thinking..."):
            try:
                # Call Azure OpenAI API with full chat history for context
                assistant_response = send_message_to_azure_openai(
                    user_input, 
                    st.session_state.current_chat[:-1]  # Pass history excluding current message
                )
                
                # Add assistant response to chat history
                assistant_message = {
                    "role": "assistant",
                    "content": assistant_response
                }
                st.session_state.current_chat.append(assistant_message)
                
                # Auto-save session after each exchange
                save_current_session()
                
            except Exception as e:
                # Handle any unexpected errors
                st.error(f"An error occurred: {str(e)}")
                error_message = {
                    "role": "assistant",
                    "content": "I apologize, but I encountered an error processing your request. Please try again."
                }
                st.session_state.current_chat.append(error_message)
        
        # Increment input key to clear the text input field
        st.session_state.input_key += 1
        
        # Rerun to display new messages immediately
        st.rerun()

# ==================== MAIN APP ====================

def main():
    """Main application entry point."""
    
    # Initialize session state
    initialize_session_state()
    
    # Route to appropriate page based on session state
    if st.session_state.page == 'home':
        home_page()
    elif st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'chat':
        # Only allow chat page if logged in or guest
        if st.session_state.logged_in:
            chat_page()
        else:
            st.error("Please login or continue as guest to access the chat.")
            navigate_to('home')
    else:
        # Default to home page
        navigate_to('home')

if __name__ == "__main__":
    main()