"""
Streamlit Chat Application for LLM HV Search
Refactored version using the new modular structure.
"""
import sys
from pathlib import Path
import streamlit as st
from typing import List, Dict, Any

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.rag import answer_question
from src.core.azure_client import is_mock_mode
from src.core.search import check_available_modes


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


def process_user_message(message: str) -> str:
    """Process user message using the conversation history from session_state."""
    # Define system prompts for different modes
    system_prompts = {
        "hr": "Eres un experto en recursos humanos y selección de personal.",
        "qa": "Eres un experto en pruebas de software, control de calidad y QA testing."
    }
    
    # Get the system prompt based on selected mode
    system_content = system_prompts.get(st.session_state.mode, system_prompts["hr"])
    
    # Ensure conversation history has system message
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": system_content
        })
    else:
        # Update system message if mode has changed
        st.session_state.messages[0]["content"] = system_content
    
    # Process the message using RAG
    return answer_question(message, st.session_state.messages, st.session_state.mode)


def initialize_session_state():
    """Initialize session state variables for the chat."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm here to help. What would you like to chat about?"
        })
    
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
                    content = ("Hello! I'm here to help with Human Resources questions using our "
                             "indexed HR documents. What would you like to know?")
                else:
                    content = ("Hello! I'm here to help with Human Resources questions. "
                             "Note: No HR documents are currently indexed, so I'll provide general assistance. "
                             "What would you like to know?")
                st.session_state.messages = [{"role": "assistant", "content": content}]
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
                    content = ("Hello! I'm here to help with QA Testing questions using our "
                             "indexed testing documents. What would you like to know?")
                else:
                    content = ("Hello! I'm here to help with QA Testing questions. "
                             "Note: No QA documents are currently indexed, so I'll provide general assistance. "
                             "What would you like to know?")
                st.session_state.messages = [{"role": "assistant", "content": content}]
                st.rerun()
        
        # Show status information
        st.markdown("### Knowledge Base Status")
        col1, col2 = st.columns(2)
        
        with col1:
            if mode_status["hr"]["available"]:
                file_count = mode_status["hr"].get("file_count", 0)
                st.success(f"✅ HR Documents: {file_count} files indexed")
                processed_files = mode_status["hr"].get("processed_files", [])
                if processed_files:
                    with st.expander("View indexed HR files"):
                        for filename in processed_files:
                            st.text(f"📄 {filename}")
            else:
                st.warning("⚠️ HR Documents: Not indexed")
                st.caption("Run `indexer_hr.py` to index HR documents")
                
        with col2:
            if mode_status["qa"]["available"]:
                file_count = mode_status["qa"].get("file_count", 0)
                st.success(f"✅ QA Documents: {file_count} files indexed")
                processed_files = mode_status["qa"].get("processed_files", [])
                if processed_files:
                    with st.expander("View indexed QA files"):
                        for filename in processed_files:
                            st.text(f"📄 {filename}")
            else:
                st.warning("⚠️ QA Documents: Not indexed")
                st.caption("Run `indexer_qa.py` to index QA documents")
                
        st.stop()  # Stop execution until mode is selected
    
    # Display current mode with knowledge status
    mode_status = get_mode_status()
    current_mode_status = mode_status[st.session_state.mode]
    mode_labels = {"hr": "🧑‍💼 Human Resources", "qa": "🧪 QA Testing"}
    status_icon = "✅" if current_mode_status["available"] else "⚠️"
    
    st.success(f"Current mode: {mode_labels[st.session_state.mode]} {status_icon}")
    
    if not current_mode_status["available"]:
        indexer_file = "indexer_hr.py" if st.session_state.mode == "hr" else "indexer_qa.py"
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
        This is a Streamlit chat application for HR and QA document search using 
        LLM and vector similarity search.
        
        **Current Features:**
        - Human Resources mode: Expert help with HR questions
        - QA Testing mode: Expert help with software testing questions
        - Document-based search when indexes are available
        - File tracking to see what documents are indexed
        """)
        
        st.header("Knowledge Base Status")
        mode_status = get_mode_status()
        
        # HR Status
        if mode_status["hr"]["available"]:
            file_count = mode_status["hr"].get("file_count", 0)
            st.success(f"✅ HR Documents: {file_count} files")
            processed_files = mode_status["hr"].get("processed_files", [])
            if processed_files and st.button("📋 View HR Files", key="hr_files"):
                st.text("\n".join(processed_files))
        else:
            st.warning("⚠️ HR Documents: Not indexed")
            
        # QA Status  
        if mode_status["qa"]["available"]:
            file_count = mode_status["qa"].get("file_count", 0)
            st.success(f"✅ QA Documents: {file_count} files")
            processed_files = mode_status["qa"].get("processed_files", [])
            if processed_files and st.button("📋 View QA Files", key="qa_files"):
                st.text("\n".join(processed_files))
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