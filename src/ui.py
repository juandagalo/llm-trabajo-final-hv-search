"""
Streamlit UI components.
"""
import streamlit as st
from . import auth
from . import llm
from . import search


def init_session():
    """Initialize session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm here to help with QA Testing questions. What would you like to know?"
        }]
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None


def add_message(role: str, content: str):
    """Add message to history."""
    st.session_state.messages.append({"role": role, "content": content})


def display_header():
    """Display app header."""
    st.title("💬 LLM HV Search Application")
    st.caption("A Streamlit chat interface for HR and QA document search")


def display_demo_warning():
    """Display demo mode warning."""
    if llm.is_mock_mode():
        st.warning("⚠️ Running in DEMO MODE - API credentials not configured.")


def display_login_status():
    """Display login status and buttons."""
    logged_in = auth.is_logged_in()
    username = auth.get_current_username()
    role = auth.get_current_role()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if logged_in:
            badge = " 👑 **ADMIN**" if role == "admin" else ""
            access = "QA + HR + Admin" if role == "admin" else "QA + HR"
            st.success(f"✅ Logged in: **{username}**{badge} | Access: **{access}**")
        else:
            st.info("ℹ️ Guest Mode | Access: **QA Only** | Login for HR access")
    
    with col2:
        if logged_in:
            if st.button("🚪 Logout", use_container_width=True):
                auth.logout()
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": "Logged out. You now have access to QA documents only."
                }]
                st.rerun()
        else:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.show_login_form = True
                st.rerun()


def display_login_form():
    """Display login form."""
    if not auth.is_logged_in() and st.session_state.get("show_login_form"):
        st.markdown("---")
        with st.form("login_form"):
            st.subheader("🔐 Login to Access HR Documents")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            submit = col1.form_submit_button("Login", use_container_width=True)
            cancel = col2.form_submit_button("Cancel", use_container_width=True)
            
            if submit:
                if auth.verify_credentials(username, password):
                    auth.login(username)
                    st.session_state.messages = [{
                        "role": "assistant",
                        "content": f"Welcome, {username}! You now have access to QA and HR documents."
                    }]
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            
            if cancel:
                st.session_state.show_login_form = False
                st.rerun()
        st.markdown("---")


def display_knowledge_status():
    """Display knowledge base status."""
    modes = search.check_available_modes()
    logged_in = auth.is_logged_in()
    
    st.markdown("### 📚 Knowledge Base Status")
    col1, col2 = st.columns(2)
    
    with col1:
        qa = modes["qa"]
        icon = "✅" if qa["available"] else "⚠️"
        st.markdown(f"**🔍 QA Documents {icon}**")
        if qa["available"]:
            st.success(f"✅ {qa['file_count']} files indexed")
            if qa["processed_files"]:
                with st.expander("View files"):
                    for f in qa["processed_files"]:
                        st.text(f"📄 {f}")
        else:
            st.warning("⚠️ Not indexed - run indexer.py qa")
    
    with col2:
        hr = modes["hr"]
        icon = "✅" if hr["available"] else "⚠️"
        lock = "" if logged_in else " (🔒 Login Required)"
        st.markdown(f"**🧑‍💼 HR Documents {icon}**{lock}")
        if hr["available"]:
            if logged_in:
                st.success(f"✅ {hr['file_count']} files indexed")
                if hr["processed_files"]:
                    with st.expander("View files"):
                        for f in hr["processed_files"]:
                            st.text(f"📄 {f}")
            else:
                st.info(f"🔒 {hr['file_count']} files (login to access)")
        else:
            st.warning("⚠️ Not indexed - run indexer.py hr")


def display_chat():
    """Display chat history."""
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


def display_sidebar():
    """Display sidebar."""
    with st.sidebar:
        st.header("About")
        st.markdown("""
        Chat app for HR and QA document search using LLM and vector similarity.
        
        **Access Levels:**
        - **Guest**: QA documents only
        - **Logged In**: QA + HR documents
        - **Admin**: Full access + Excel editing for all users
        """)
        
        # Access info
        st.header("Access")
        logged_in = auth.is_logged_in()
        if logged_in:
            role = auth.get_current_role()
            badge = " 👑" if role == "admin" else ""
            st.success(f"✅ {auth.get_current_username()}{badge}")
            access = ["✅ QA Documents", "✅ HR Documents", "📊 Excel Editing"]
            if role == "admin":
                access.append("👑 Admin Access")
            st.info("📚 Access:\n- " + "\n- ".join(access))
        else:
            st.info("👤 Guest Mode")
            st.warning("📚 Access:\n- ✅ QA Documents\n- 🔒 HR (login required)\n- 🔒 Excel (login required)")
        
        # Knowledge status
        st.header("Knowledge Base")
        modes = search.check_available_modes()
        for mode, info in modes.items():
            if info["available"]:
                st.success(f"✅ {mode.upper()}: {info['file_count']} files")
            else:
                st.warning(f"⚠️ {mode.upper()}: Not indexed")
        
        # Chat controls
        st.header("Controls")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            access_msg = "QA and HR" if logged_in else "QA"
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Chat cleared! I can help with {access_msg} documents."
            }]
            st.rerun()
