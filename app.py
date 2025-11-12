"""
Streamlit Chat Application for LLM HV Search
Refactored version using the new modular structure with login-based access control.
"""
import sys
import os
from pathlib import Path
import streamlit as st
from typing import List, Dict, Any
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.rag import answer_question
from src.core.azure_client import is_mock_mode
from src.core.search import check_available_modes, search


def load_credentials():
    """Load user credentials from environment variables or Streamlit secrets."""
    try:
        users_string = ""
        
        # Try to get from environment variable first (for local development)
        users_string = os.getenv('APP_USERS', '')
        
        # If not found in env vars, try Streamlit secrets (for deployment)
        if not users_string:
            try:
                if hasattr(st, 'secrets') and 'APP_USERS' in st.secrets:
                    users_string = st.secrets['APP_USERS']
            except Exception:
                # Secrets not available, continue with empty string
                pass
        
        if not users_string:
            st.error("⚠️ No user credentials configured! Please set APP_USERS in your .env file or Streamlit secrets.")
            return []
        
        # Parse the credentials string (format: username1:password1,username2:password2)
        users = []
        for user_pair in users_string.split(','):
            if ':' in user_pair:
                username, password = user_pair.strip().split(':', 1)
                users.append({
                    "username": username.strip(),
                    "password": password.strip()
                })
                print(f"Loaded user: {username.strip()}")
        
        return users
    except Exception as e:
        st.error(f"⚠️ Error loading credentials: {str(e)}")
        return []


def verify_credentials(username: str, password: str) -> bool:
    """Verify if username and password match credentials."""
    users = load_credentials()
    for user in users:
        if user.get("username") == username and user.get("password") == password:
            return True
    return False


def get_mode_status():
    """Get the current knowledge status for each mode."""
    try:
        modes = check_available_modes()
        return {
            "hr": {
                "available": modes["hr"]["available"],
                "description": modes["hr"]["description"],
                "file_count": modes["hr"]["file_count"],
                "processed_files": modes["hr"]["processed_files"]
            },
            "qa": {
                "available": modes["qa"]["available"], 
                "description": modes["qa"]["description"],
                "file_count": modes["qa"]["file_count"],
                "processed_files": modes["qa"]["processed_files"]
            }
        }
    except Exception as e:
        # Fallback if there's an error checking modes
        return {
            "hr": {
                "available": False, 
                "description": "Status unknown",
                "file_count": 0,
                "processed_files": []
            },
            "qa": {
                "available": False, 
                "description": "Status unknown",
                "file_count": 0,
                "processed_files": []
            }
        }


def answer_question_with_access_control(query: str, conversation_history: List[Dict[str, str]], is_logged_in: bool) -> str:
    """
    Answer a question with access control - searches QA only or QA+HR based on login status.
    
    Args:
        query: User's question
        conversation_history: List of conversation messages
        is_logged_in: Whether user is logged in (True = access to both QA+HR, False = QA only)
        
    Returns:
        Generated answer
    """
    from src.core.azure_client import get_azure_client, get_chat_model
    import pandas as pd
    
    if is_mock_mode():
        # Return mock response based on access level
        if is_logged_in:
            response = (f"[DEMO MODE - Full Access] Regarding '{query}': "
                       "This would search both QA Testing and HR documents to provide comprehensive answers "
                       "from both knowledge bases. You have access to information about software testing, "
                       "quality assurance, human resources, hiring, and workplace policies.")
        else:
            response = (f"[DEMO MODE - QA Access Only] Regarding '{query}': "
                       "This would search QA Testing documents to provide answers about software testing, "
                       "quality assurance methodologies, test automation, and testing best practices. "
                       "Login to access HR documents as well.")
        return response
    
    # Check which indexes are available
    mode_status = get_mode_status()
    qa_available = mode_status["qa"]["available"]
    hr_available = mode_status["hr"]["available"]
    
    context_documents = []
    
    # Perform document search based on access level and availability
    try:
        if is_logged_in:
            # Search both QA and HR documents if available
            if qa_available and hr_available:
                qa_results = search(query, mode="qa", k=5)
                hr_results = search(query, mode="hr", k=5)
                
                # Combine results
                combined_results = pd.concat([qa_results, hr_results], ignore_index=True)
                combined_results = combined_results.sort_values("cosine_similarity", ascending=False).head(10)
                context_documents = list(combined_results['text'].values)
            elif qa_available:
                # Only QA available
                qa_results = search(query, mode="qa", k=10)
                context_documents = list(qa_results['text'].values)
            elif hr_available:
                # Only HR available
                hr_results = search(query, mode="hr", k=10)
                context_documents = list(hr_results['text'].values)
        else:
            # Search only QA documents (guest mode)
            if qa_available:
                qa_results = search(query, mode="qa", k=10)
                context_documents = list(qa_results['text'].values)
    except Exception as e:
        # If search fails, provide a response without context
        st.warning(f"⚠️ Could not search documents: {str(e)}")
    
    # Create prompt with or without context
    if context_documents:
        context = "\n\n".join(context_documents)
        prompt = (f"Contexto:\n{context}\n\n"
                 f"Pregunta: {query}\n"
                 f"Respuesta:")
    else:
        # No context available - general response
        if is_logged_in:
            prompt = (f"No hay documentos indexados disponibles. Responde de manera general como experto en QA y HR.\n\n"
                     f"Pregunta: {query}\n"
                     f"Respuesta:")
        else:
            prompt = (f"No hay documentos indexados disponibles. Responde de manera general como experto en QA.\n\n"
                     f"Pregunta: {query}\n"
                     f"Respuesta:")
    
    temp_conversation = conversation_history.copy()
    temp_conversation.append({"role": "user", "content": prompt})
    
    # Generate response
    client = get_azure_client()
    model = get_chat_model()
    
    response = client.chat.completions.create(
        model=model,
        messages=temp_conversation
    )
    
    assistant_reply = response.choices[0].message.content
    return assistant_reply


def process_user_message(message: str) -> str:
    """Process user message using the conversation history from session_state."""
    # Determine access level based on login status
    is_logged_in = st.session_state.get("is_logged_in", False)
    
    # Define system prompt based on access level
    if is_logged_in:
        system_content = ("Eres un experto en recursos humanos, selección de personal, "
                         "pruebas de software, control de calidad y QA testing.")
    else:
        system_content = "Eres un experto en pruebas de software, control de calidad y QA testing. Tienes prohibido responder preguntas sobre recursos humanos en cualquier ambito."
    
    # Ensure conversation history has system message
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": system_content
        })
    else:
        # Update system message if login state has changed
        st.session_state.messages[0]["content"] = system_content
    
    # Process the message using RAG with combined search if logged in
    return answer_question_with_access_control(message, st.session_state.messages, is_logged_in)


def initialize_session_state():
    """Initialize session state variables for the chat."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm here to help with QA Testing questions. What would you like to know?"
        })
    
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    
    if "username" not in st.session_state:
        st.session_state.username = None


def display_chat_history():
    """Display the chat history."""
    for message in st.session_state.messages:
        # Skip system messages - only show user and assistant messages
        if message["role"] in ["user", "assistant"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="LLM HV Search Application",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 LLM HV Search Application")
    st.caption("A Streamlit chat interface for HR and QA document search")
    
    # Show demo mode warning if in mock mode
    if is_mock_mode():
        st.warning("⚠️ Running in DEMO MODE - Azure OpenAI credentials not configured. "
                  "Responses are simulated for demonstration purposes.")
    
    # Initialize session state
    initialize_session_state()
    
    # Display login status and access level
    is_logged_in = st.session_state.get("is_logged_in", False)
    
    # Create header with login status badge
    col1, col2 = st.columns([3, 1])
    with col1:
        if is_logged_in:
            st.success(f"✅ Logged in as: **{st.session_state.username}** | Access: **QA + HR Documents**")
        else:
            st.info("ℹ️ Guest Mode | Access: **QA Documents Only** | Login for HR access")
    with col2:
        if is_logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.is_logged_in = False
                st.session_state.username = None
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": "You've been logged out. Chat history has been cleared for security. You now have access to QA documents only."
                }]
                st.rerun()
        else:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.show_login_form = True
                st.rerun()
    
    # Show login form if requested
    if not is_logged_in and st.session_state.get("show_login_form", False):
        st.markdown("---")
        with st.form("login_form"):
            st.subheader("🔐 Login to Access HR Documents")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if submit:
                if verify_credentials(username, password):
                    st.session_state.is_logged_in = True
                    st.session_state.username = username
                    st.session_state.show_login_form = False
                    st.session_state.messages = [{
                        "role": "assistant",
                        "content": f"Welcome back, {username}! You now have access to both QA and HR documents. What would you like to know?"
                    }]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            
            if cancel:
                st.session_state.show_login_form = False
                st.rerun()
        st.markdown("---")
    
    # Get mode status
    mode_status = get_mode_status()
    
    # Show knowledge base status
    st.markdown("### 📚 Knowledge Base Status")
    col1, col2 = st.columns(2)
    
    with col1:
        qa_status = mode_status["qa"]
        qa_icon = "✅" if qa_status["available"] else "⚠️"
        st.markdown(f"**� QA Documents {qa_icon}**")
        if qa_status["available"]:
            file_count = qa_status.get("file_count", 0)
            st.success(f"✅ {file_count} files indexed")
            processed_files = qa_status.get("processed_files", [])
            if processed_files:
                with st.expander("View indexed QA files"):
                    for filename in processed_files:
                        st.text(f"📄 {filename}")
        else:
            st.warning("⚠️ Not indexed")
            st.caption("Run `indexer_qa.py` to index QA documents")
    
    with col2:
        hr_status = mode_status["hr"]
        hr_icon = "✅" if hr_status["available"] else "⚠️"
        if is_logged_in:
            st.markdown(f"**🧑‍💼 HR Documents {hr_icon}** (Access Granted)")
        else:
            st.markdown(f"**🧑‍💼 HR Documents {hr_icon}** (🔒 Login Required)")
        
        if hr_status["available"]:
            file_count = hr_status.get("file_count", 0)
            if is_logged_in:
                st.success(f"✅ {file_count} files indexed")
            else:
                st.info(f"🔒 {file_count} files (Login to access)")
            processed_files = hr_status.get("processed_files", [])
            if processed_files and is_logged_in:
                with st.expander("View indexed HR files"):
                    for filename in processed_files:
                        st.text(f"📄 {filename}")
        else:
            st.warning("⚠️ Not indexed")
            st.caption("Run `indexer_hr.py` to index HR documents")
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("What would you like to ask?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the message and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_user_message(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This is a Streamlit chat application for HR and QA document search using 
        LLM and vector similarity search.
        
        **Access Levels:**
        - **Guest Mode**: Access to QA Testing documents only
        - **Logged In**: Access to both QA Testing and HR documents
        
        **Features:**
        - Login-based access control
        - Combined document search when logged in
        - Document-based RAG responses
        - File tracking to see what documents are indexed
        """)
        
        st.header("Access Information")
        if is_logged_in:
            st.success(f"✅ **Logged in as:** {st.session_state.username}")
            st.info("📚 **Your Access:**\n- ✅ QA Testing Documents\n- ✅ HR Documents")
        else:
            st.info("👤 **Guest Mode**")
            st.warning("📚 **Your Access:**\n- ✅ QA Testing Documents\n- 🔒 HR Documents (Login required)")
        
        st.header("Knowledge Base Status")
        mode_status = get_mode_status()
        
        # QA Status
        if mode_status["qa"]["available"]:
            file_count = mode_status["qa"].get("file_count", 0)
            st.success(f"✅ QA Documents: {file_count} files")
        else:
            st.warning("⚠️ QA Documents: Not indexed")
        
        # HR Status
        if mode_status["hr"]["available"]:
            file_count = mode_status["hr"].get("file_count", 0)
            if is_logged_in:
                st.success(f"✅ HR Documents: {file_count} files")
            else:
                st.info(f"� HR Documents: {file_count} files (Login required)")
        else:
            st.warning("⚠️ HR Documents: Not indexed")
            
        if not mode_status["hr"]["available"] or not mode_status["qa"]["available"]:
            st.caption("Run the appropriate indexer script to enable document search")
        
        st.header("Chat Controls")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            access_msg = "both QA and HR documents" if is_logged_in else "QA documents"
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Chat history cleared! I'm here to help with {access_msg}. What would you like to know?"
            }]
            st.rerun()


if __name__ == "__main__":
    main()