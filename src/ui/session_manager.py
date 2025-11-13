"""
Session State Management for LLM HV Search application.
Handles initialization and management of Streamlit session state.
"""
import streamlit as st
from typing import List, Dict


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


def ensure_system_message(system_content: str):
    """Ensure conversation history has correct system message."""
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": system_content
        })
    else:
        # Update system message if login state has changed
        st.session_state.messages[0]["content"] = system_content


def add_user_message(content: str):
    """Add a user message to the chat history."""
    st.session_state.messages.append({"role": "user", "content": content})


def add_assistant_message(content: str):
    """Add an assistant message to the chat history."""
    st.session_state.messages.append({"role": "assistant", "content": content})


def clear_chat_history(welcome_message: str):
    """Clear chat history and set a new welcome message."""
    st.session_state.messages = [{
        "role": "assistant",
        "content": welcome_message
    }]


def get_conversation_history() -> List[Dict[str, str]]:
    """Get the current conversation history."""
    return st.session_state.messages.copy()


def get_session_value(key: str, default=None):
    """Get a value from session state."""
    return st.session_state.get(key, default)


def set_session_value(key: str, value):
    """Set a value in session state."""
    st.session_state[key] = value