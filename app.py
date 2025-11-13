"""
Streamlit Chat Application for LLM HV Search
Refactored version using modular structure with login-based access control.
"""
import sys
import os
from pathlib import Path
import streamlit as st

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our modular components
from src.ui.components import (
    display_header, display_demo_warning, display_login_status,
    display_login_form, display_knowledge_base_status, display_chat_history,
    display_sidebar
)
from src.ui.session_manager import initialize_session_state, add_user_message, add_assistant_message
from src.core.chat_handler import process_user_message





def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="LLM HV Search Application",
        page_icon="💬",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Display UI components
    display_header()
    display_demo_warning()
    display_login_status()
    display_login_form()
    display_knowledge_base_status()
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("What would you like to ask?"):
        # Add user message to chat history and display it
        add_user_message(prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the message and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_user_message(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        add_assistant_message(response)
    
    # Display sidebar
    display_sidebar()


if __name__ == "__main__":
    main()