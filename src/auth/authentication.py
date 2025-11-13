"""
Authentication module for LLM HV Search application.
Handles user credentials, login verification, and access control.
"""
import os
import streamlit as st
from typing import List, Dict


def load_credentials() -> List[Dict[str, str]]:
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


def is_user_logged_in() -> bool:
    """Check if a user is currently logged in."""
    return st.session_state.get("is_logged_in", False)


def get_current_username() -> str:
    """Get the current logged-in username."""
    return st.session_state.get("username", "")


def login_user(username: str) -> None:
    """Log in a user by setting session state."""
    st.session_state.is_logged_in = True
    st.session_state.username = username
    st.session_state.show_login_form = False


def logout_user() -> None:
    """Log out the current user and clear session state."""
    st.session_state.is_logged_in = False
    st.session_state.username = None
    if 'show_login_form' in st.session_state:
        del st.session_state.show_login_form


def get_user_access_level() -> str:
    """Get the access level description for the current user."""
    if is_user_logged_in():
        return "QA + HR Documents"
    else:
        return "QA Documents Only"


def get_system_message_content() -> str:
    """Get the appropriate system message content based on login status."""
    if is_user_logged_in():
        return ("Eres un experto en recursos humanos, selección de personal, "
                "pruebas de software, control de calidad y QA testing.")
    else:
        return "Eres un experto en pruebas de software, control de calidad y QA testing. Tienes prohibido responder preguntas sobre recursos humanos en cualquier ambito."