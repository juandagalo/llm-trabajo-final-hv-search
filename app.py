"""
Streamlit Chat Application for LLM HV Search
"""
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from src.ui import (
    init_session, add_message, display_header, display_demo_warning,
    display_login_status, display_login_form, display_knowledge_status,
    display_chat, display_sidebar
)
from src.chat import process_message


def main():
    st.set_page_config(
        page_title="LLM HV Search",
        page_icon="💬",
        layout="wide"
    )
    
    init_session()
    
    display_header()
    display_demo_warning()
    display_login_status()
    display_login_form()
    display_knowledge_status()
    display_chat()
    
    if prompt := st.chat_input("What would you like to ask?"):
        add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_message(prompt)
            st.markdown(response)
        
        add_message("assistant", response)
    
    display_sidebar()


if __name__ == "__main__":
    main()