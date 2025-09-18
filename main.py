import streamlit as st
from typing import List, Dict, Any
from RagSearch import answer_question
from azure_client import is_mock_mode
from recuperacion_consulta_faiss import check_available_modes

def process_user_message(message: str) -> str:
    """
    Procesa el mensaje del usuario usando el historial de conversación de session_state.
    """
    # Define system prompts for different modes
    system_prompts = {
        "hr": "Eres un experto en recursos humanos y selección de personal.",
        "qa": "Eres un experto en pruebas de software, control de calidad y QA testing."
    }
    
    # Get the system prompt based on selected mode
    system_content = system_prompts.get(st.session_state.mode, system_prompts["hr"])
    
    # Asegura que el historial tenga el mensaje system si está vacío
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": system_content
        })
    else:
        # Update system message if mode has changed
        st.session_state.messages[0]["content"] = system_content
    
    # Pasa el historial a answer_question (se modifica en el propio método)
    return answer_question(message, st.session_state.messages, st.session_state.mode)


def get_mode_status():
    """Get the current knowledge status for each mode."""
    try:
        modes = check_available_modes()
        return {
            "hr": {
                "available": modes["hr"]["available"],
                "description": "Human Resources documents" if modes["hr"]["available"] else "No HR documents indexed"
            },
            "qa": {
                "available": modes["qa"]["available"], 
                "description": "QA Testing documents" if modes["qa"]["available"] else "No QA documents indexed"
            }
        }
    except Exception as e:
        # Fallback if there's an error checking modes
        return {
            "hr": {"available": False, "description": "Status unknown"},
            "qa": {"available": False, "description": "Status unknown"}
        }


def initialize_session_state():
    """Initialize session state variables for the chat."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm here to help. What would you like to chat about?"
        })
    
    # Initialize mode selection if not exists
    if "mode" not in st.session_state:
        st.session_state.mode = None


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
    
    # Show demo mode warning if in mock mode
    if is_mock_mode():
        st.warning("⚠️ Running in DEMO MODE - Azure OpenAI credentials not configured. Responses are simulated for demonstration purposes.")
    
    # Initialize session state
    initialize_session_state()
    
    # Mode selection interface
    if st.session_state.mode is None:
        st.info("Please select the application mode to continue:")
        
        # Get mode status
        mode_status = get_mode_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # HR Mode button with status
            hr_status = mode_status["hr"]
            hr_icon = "✅" if hr_status["available"] else "⚠️"
            hr_label = f"🧑‍💼 Human Resources {hr_icon}"
            hr_help = f"{hr_status['description']}"
            
            if st.button(hr_label, use_container_width=True, help=hr_help):
                st.session_state.mode = "hr"
                if hr_status["available"]:
                    content = "Hello! I'm here to help with Human Resources questions using our indexed HR documents. What would you like to know?"
                else:
                    content = "Hello! I'm here to help with Human Resources questions. Note: No HR documents are currently indexed, so I'll provide general assistance. What would you like to know?"
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": content
                }]
                st.rerun()
                
        with col2:
            # QA Mode button with status
            qa_status = mode_status["qa"]
            qa_icon = "✅" if qa_status["available"] else "⚠️"
            qa_label = f"🧪 QA Testing {qa_icon}"
            qa_help = f"{qa_status['description']}"
            
            if st.button(qa_label, use_container_width=True, help=qa_help):
                st.session_state.mode = "qa"
                if qa_status["available"]:
                    content = "Hello! I'm here to help with QA Testing questions using our indexed testing documents. What would you like to know?"
                else:
                    content = "Hello! I'm here to help with QA Testing questions. Note: No QA documents are currently indexed, so I'll provide general assistance. What would you like to know?"
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": content
                }]
                st.rerun()
        
        # Show status information
        st.markdown("### Knowledge Base Status")
        col1, col2 = st.columns(2)
        
        with col1:
            if mode_status["hr"]["available"]:
                st.success("✅ HR Documents: Available")
            else:
                st.warning("⚠️ HR Documents: Not indexed")
                st.caption("Run `indexerHR.py` to index HR documents")
                
        with col2:
            if mode_status["qa"]["available"]:
                st.success("✅ QA Documents: Available") 
            else:
                st.warning("⚠️ QA Documents: Not indexed")
                st.caption("Run `indexerQA.py` to index QA documents")
                
        st.stop()  # Stop execution until mode is selected
    
    # Display current mode with knowledge status
    mode_status = get_mode_status()
    current_mode_status = mode_status[st.session_state.mode]
    mode_labels = {"hr": "🧑‍💼 Human Resources", "qa": "🧪 QA Testing"}
    status_icon = "✅" if current_mode_status["available"] else "⚠️"
    
    st.success(f"Current mode: {mode_labels[st.session_state.mode]} {status_icon}")
    
    if not current_mode_status["available"]:
        indexer_file = "indexerHR.py" if st.session_state.mode == "hr" else "indexerQA.py"
        st.info(f"💡 To enable document search for this mode, run `{indexer_file}` to index your documents.")
    
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
        
        **Current Features:**
        - Human Resources mode: Expert help with HR questions
        - QA Testing mode: Expert help with software testing questions
        
        **To customize:**
        1. Edit the `process_user_message()` function in `main.py`
        2. Add your custom logic for generating responses
        3. Install any additional dependencies in `requirements.txt`
        """)
        
        st.header("Knowledge Base Status")
        mode_status = get_mode_status()
        
        # HR Status
        if mode_status["hr"]["available"]:
            st.success("✅ HR Documents: Indexed")
        else:
            st.warning("⚠️ HR Documents: Not indexed")
            
        # QA Status  
        if mode_status["qa"]["available"]:
            st.success("✅ QA Documents: Indexed")
        else:
            st.warning("⚠️ QA Documents: Not indexed")
            
        if not mode_status["hr"]["available"] or not mode_status["qa"]["available"]:
            st.caption("Run the appropriate indexer script to enable document search")
        
        st.header("Chat Controls")
        if st.button("Clear Chat History"):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Hello! I'm here to help. What would you like to chat about?"
            }]
            st.rerun()
            
        if st.button("Change Mode"):
            st.session_state.mode = None
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()