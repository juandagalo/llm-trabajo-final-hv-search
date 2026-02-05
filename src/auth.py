"""
Authentication for LLM HV Search application.
"""
import os
import streamlit as st


def load_credentials() -> list:
    """Load user credentials from environment or Streamlit secrets."""
    users_string = os.getenv('APP_USERS', '')
    
    if not users_string:
        try:
            if hasattr(st, 'secrets') and 'APP_USERS' in st.secrets:
                users_string = st.secrets['APP_USERS']
        except:
            pass
    
    if not users_string:
        return []
    
    users = []
    for user_pair in users_string.split(','):
        parts = user_pair.strip().split(':')
        if len(parts) >= 2:
            users.append({
                "username": parts[0].strip(),
                "password": parts[1].strip(),
                "role": parts[2].strip().lower() if len(parts) >= 3 else 'user'
            })
    return users


def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password."""
    for user in load_credentials():
        if user["username"] == username and user["password"] == password:
            return True
    return False


def get_user_role(username: str) -> str:
    """Get user's role."""
    for user in load_credentials():
        if user["username"] == username:
            return user.get("role", "user")
    return "user"


def is_admin(username: str = None) -> bool:
    """Check if user is admin."""
    if username is None:
        username = get_current_username()
    return get_user_role(username) == "admin" if username else False


def is_logged_in() -> bool:
    """Check if user is logged in."""
    return st.session_state.get("is_logged_in", False)


def get_current_username() -> str:
    """Get current username."""
    return st.session_state.get("username", "")


def get_current_role() -> str:
    """Get current user's role."""
    username = get_current_username()
    return get_user_role(username) if username else "guest"


def login(username: str):
    """Log in a user."""
    st.session_state.is_logged_in = True
    st.session_state.username = username
    st.session_state.user_role = get_user_role(username)
    st.session_state.show_login_form = False


def logout():
    """Log out current user."""
    st.session_state.is_logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.pop('show_login_form', None)


def get_system_prompt() -> str:
    """Get system prompt based on access level."""
    if is_logged_in():
        if is_admin():
            return ("Eres un experto en recursos humanos, selección de personal, "
                   "pruebas de software, control de calidad y QA testing. "
                   "Además, tienes acceso administrativo completo.")
        return ("Eres un experto en recursos humanos, selección de personal, "
                "pruebas de software, control de calidad y QA testing.")
    return ("Eres un experto en pruebas de software, control de calidad y QA testing. "
            "Tienes prohibido responder preguntas sobre recursos humanos.")
