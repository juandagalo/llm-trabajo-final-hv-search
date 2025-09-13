import streamlit as st
from typing import List, Dict, Any
# Integración real con RagSearch
from RagSearch import answer_question

def process_user_message(message: str) -> str:
    """
    Procesa el mensaje del usuario usando el historial de conversación de session_state.
    """
    # Asegura que el historial tenga el mensaje system si está vacío
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": "Eres un experto en recursos humanos y selección de personal."
        })
    # Pasa el historial a answer_question (se modifica en el propio método)
    return answer_question(message, st.session_state.messages)


def initialize_session_state():
    """Initialize session state variables for the chat."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm here to help. What would you like to chat about?"
        })


def display_chat_history():
    """Display the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="LLM Chat Application",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 LLM Chat Application")
    st.caption("A Streamlit chat interface for your LLM work")
    
    # Initialize session state
    initialize_session_state()
    
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
        This is a Streamlit chat application that you can use as a foundation 
        for your LLM project.
        
        **To customize:**
        1. Edit the `process_user_message()` function in `main.py`
        2. Add your custom logic for generating responses
        3. Install any additional dependencies in `requirements.txt`
        """)
        
        st.header("Chat Controls")
        if st.button("Clear Chat History"):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Hello! I'm here to help. What would you like to chat about?"
            }]
            st.rerun()


if __name__ == "__main__":
    main()