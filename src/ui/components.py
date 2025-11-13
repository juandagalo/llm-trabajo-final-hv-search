"""
UI Components for LLM HV Search application.
Contains all Streamlit UI components and display functions.
"""
import streamlit as st
from typing import Dict, Any
from ..auth.authentication import is_user_logged_in, get_current_username, verify_credentials, login_user, logout_user, get_current_user_role, is_admin_user
from ..core.search import check_available_modes


def display_header():
    """Display the main application header."""
    st.title("💬 LLM HV Search Application")
    st.caption("A Streamlit chat interface for HR and QA document search")


def display_demo_warning():
    """Display demo mode warning if in mock mode."""
    from ..core.azure_client import is_mock_mode
    if is_mock_mode():
        st.warning("⚠️ Running in DEMO MODE - Azure OpenAI credentials not configured. "
                  "Responses are simulated for demonstration purposes.")


def display_login_status():
    """Display login status and login/logout buttons."""
    is_logged_in = is_user_logged_in()
    username = get_current_username()
    user_role = get_current_user_role()
    
    # Create header with login status badge
    col1, col2 = st.columns([3, 1])
    with col1:
        if is_logged_in:
            role_badge = " 👑 **ADMIN**" if user_role == "admin" else ""
            access_level = "QA + HR Documents + Admin Access" if user_role == "admin" else "QA + HR Documents"
            st.success(f"✅ Logged in as: **{username}**{role_badge} | Access: **{access_level}**")
        else:
            st.info("ℹ️ Guest Mode | Access: **QA Documents Only** | Login for HR access")
    with col2:
        if is_logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": "You've been logged out. Chat history has been cleared for security. You now have access to QA documents only."
                }]
                st.rerun()
        else:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.show_login_form = True
                st.rerun()


def display_login_form():
    """Display the login form when requested."""
    if not is_user_logged_in() and st.session_state.get("show_login_form", False):
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
                    login_user(username)
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


def display_knowledge_base_status():
    """Display the status of available knowledge bases."""
    mode_status = check_available_modes()
    is_logged_in = is_user_logged_in()
    
    st.markdown("### 📚 Knowledge Base Status")
    col1, col2 = st.columns(2)
    
    with col1:
        qa_status = mode_status["qa"]
        qa_icon = "✅" if qa_status["available"] else "⚠️"
        st.markdown(f"**🔍 QA Documents {qa_icon}**")
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


def display_chat_history():
    """Display the chat history."""
    for message in st.session_state.messages:
        # Skip system messages - only show user and assistant messages
        if message["role"] in ["user", "assistant"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


def display_sidebar():
    """Display the sidebar with information and controls."""
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
        - Excel editing (logged-in users only)
        """)
        
        _display_sidebar_access_info()
        _display_sidebar_knowledge_status()
        _display_sidebar_excel_info()
        _display_sidebar_chat_controls()


def _display_sidebar_access_info():
    """Display access information in sidebar."""
    is_logged_in = is_user_logged_in()
    username = get_current_username()
    
    st.header("Access Information")
    user_role = get_current_user_role()
    
    if is_logged_in:
        role_badge = " 👑" if user_role == "admin" else ""
        st.success(f"✅ **Logged in as:** {username}{role_badge}")
        
        access_items = ["- ✅ QA Testing Documents", "- ✅ HR Documents", "- 📊 Excel Editing"]
        if user_role == "admin":
            access_items.append("- 👑 Admin Access (All Users)")
            
        st.info("📚 **Your Access:**\n" + "\n".join(access_items))
    else:
        st.info("👤 **Guest Mode**")
        st.warning("📚 **Your Access:**\n- ✅ QA Testing Documents\n- 🔒 HR Documents (Login required)\n- 🔒 Excel Editing (Login required)")


def _display_sidebar_knowledge_status():
    """Display knowledge base status in sidebar."""
    st.header("Knowledge Base Status")
    mode_status = check_available_modes()
    is_logged_in = is_user_logged_in()
    
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
            st.info(f"🔒 HR Documents: {file_count} files (Login required)")
    else:
        st.warning("⚠️ HR Documents: Not indexed")
        
    if not mode_status["hr"]["available"] or not mode_status["qa"]["available"]:
        st.caption("Run the appropriate indexer script to enable document search")


def _display_sidebar_excel_info():
    """Display Excel functionality information in sidebar."""
    is_logged_in = is_user_logged_in()
    user_role = get_current_user_role()
    
    st.header("Excel Functions")
    if is_logged_in:
        if user_role == "admin":
            st.success("📊 Excel editing enabled 👑 Admin")
        else:
            st.success("📊 Excel editing enabled")
            
        with st.expander("Excel Commands"):
            basic_commands = """
            **Available Excel files:**
            - employee_data.xlsx
            - project_tracker.xlsx
            - time_tracking.xlsx
            - performance_review.xlsx
            
            **Personal commands:**
            - "Update my status to completed in project_tracker.xlsx"
            - "Set my progress to 75% in project_tracker.xlsx"  
            - "Show my data in employee_data.xlsx"
            - "Change my department to IT in employee_data.xlsx"
            """
            
            admin_commands = """
            
            **Admin commands:**
            - "Update juan's status to completed in project_tracker.xlsx"
            - "Show maria's data in employee_data.xlsx"
            - "Show all users in project_tracker.xlsx"
            - "Set carlos' progress to 90% in project_tracker.xlsx"
            """
            
            if user_role == "admin":
                st.markdown(basic_commands + admin_commands)
            else:
                st.markdown(basic_commands)
    else:
        st.info("🔒 Excel editing requires login")


def _display_sidebar_chat_controls():
    """Display chat controls in sidebar."""
    is_logged_in = is_user_logged_in()
    
    st.header("Chat Controls")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        access_msg = "both QA and HR documents" if is_logged_in else "QA documents"
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Chat history cleared! I'm here to help with {access_msg}. What would you like to know?"
        }]
        st.rerun()