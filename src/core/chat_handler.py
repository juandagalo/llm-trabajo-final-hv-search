"""
Chat Handler for LLM HV Search application.
Contains the main chat processing logic and message handling.
"""
import streamlit as st
from typing import List, Dict, Any
import pandas as pd
from .azure_client import get_azure_client, get_chat_model, is_mock_mode
from .search import check_available_modes, search
from ..auth.authentication import is_user_logged_in, get_system_message_content
from ..ui.session_manager import ensure_system_message, get_conversation_history


def get_mode_status() -> Dict[str, Any]:
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


def answer_question_with_access_control(query: str, conversation_history: List[Dict[str, str]], is_logged_in: bool) -> str:
    """
    Answer a question with access control - searches QA only or QA+HR based on login status.
    
    Args:
        query: User's question
        conversation_history: List of conversation messages
        is_logged_in: Whether user is logged in (True = access to both QA+HR, False = QA only)
        
    Returns:
        Generated answer
    """
    if is_mock_mode():
        # Return mock response based on access level
        if is_logged_in:
            response = (f"[DEMO MODE - Full Access] Regarding '{query}': "
                       "This would search both QA Testing and HR documents to provide comprehensive answers "
                       "from both knowledge bases. You have access to information about software testing, "
                       "quality assurance, human resources, hiring, and workplace policies.")
        else:
            response = (f"[DEMO MODE - QA Access Only] Regarding '{query}': "
                       "This would search QA Testing documents to provide answers about software testing, "
                       "quality assurance methodologies, test automation, and testing best practices. "
                       "Login to access HR documents as well.")
        return response
    
    # Check which indexes are available
    mode_status = get_mode_status()
    qa_available = mode_status["qa"]["available"]
    hr_available = mode_status["hr"]["available"]
    
    context_documents = []
    
    # Perform document search based on access level and availability
    try:
        if is_logged_in:
            # Search both QA and HR documents if available
            if qa_available and hr_available:
                qa_results = search(query, mode="qa", k=5)
                hr_results = search(query, mode="hr", k=5)
                
                # Combine results
                combined_results = pd.concat([qa_results, hr_results], ignore_index=True)
                combined_results = combined_results.sort_values("cosine_similarity", ascending=False).head(10)
                context_documents = list(combined_results['text'].values)
            elif qa_available:
                # Only QA available
                qa_results = search(query, mode="qa", k=10)
                context_documents = list(qa_results['text'].values)
            elif hr_available:
                # Only HR available
                hr_results = search(query, mode="hr", k=10)
                context_documents = list(hr_results['text'].values)
        else:
            # Search only QA documents (guest mode)
            if qa_available:
                qa_results = search(query, mode="qa", k=10)
                context_documents = list(qa_results['text'].values)
    except Exception as e:
        # If search fails, provide a response without context
        st.warning(f"⚠️ Could not search documents: {str(e)}")
    
    # Create prompt with or without context
    if context_documents:
        context = "\n\n".join(context_documents)
        prompt = (f"Contexto:\n{context}\n\n"
                 f"Pregunta: {query}\n"
                 f"Respuesta:")
    else:
        # No context available - general response
        if is_logged_in:
            prompt = (f"No hay documentos indexados disponibles. Responde de manera general como experto en QA y HR.\n\n"
                     f"Pregunta: {query}\n"
                     f"Respuesta:")
        else:
            prompt = (f"No hay documentos indexados disponibles. Responde de manera general como experto en QA.\n\n"
                     f"Pregunta: {query}\n"
                     f"Respuesta:")
    
    temp_conversation = conversation_history.copy()
    temp_conversation.append({"role": "user", "content": prompt})
    
    # Generate response
    client = get_azure_client()
    model = get_chat_model()
    
    response = client.chat.completions.create(
        model=model,
        messages=temp_conversation
    )
    
    assistant_reply = response.choices[0].message.content
    return assistant_reply


def process_user_message(message: str) -> str:
    """Process user message using the conversation history from session_state."""
    # Determine access level based on login status
    is_logged_in = is_user_logged_in()
    
    # Define system prompt based on access level
    system_content = get_system_message_content()
    
    # Ensure conversation history has system message
    ensure_system_message(system_content)
    
    # Process the message using RAG with combined search if logged in
    conversation_history = get_conversation_history()
    return answer_question_with_access_control(message, conversation_history, is_logged_in)