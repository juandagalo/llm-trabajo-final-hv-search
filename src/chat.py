"""
Chat handler - processes user messages with RAG.
"""
import streamlit as st
import pandas as pd
from . import llm
from . import auth
from . import search as search_module
from .excel import handle_excel_command


def get_conversation_history() -> list:
    """Get conversation history."""
    return st.session_state.get("messages", []).copy()


def ensure_system_message(content: str):
    """Ensure system message is set."""
    if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {"role": "system", "content": content})
    else:
        st.session_state.messages[0]["content"] = content


def is_excel_command(message: str) -> bool:
    """Detect Excel-related commands."""
    keywords = ['excel', '.xlsx', 'update', 'edit', 'modify', 'change',
                'show my data', 'my status', 'my progress', 'set my',
                'update my', 'change my', 'project_tracker', 'employee_data',
                'time_tracking', 'performance_review']
    return any(kw in message.lower() for kw in keywords)


def answer_question(query: str, conversation: list, logged_in: bool) -> str:
    """Answer a question using RAG."""
    if llm.is_mock_mode():
        if logged_in:
            return f"[DEMO MODE - Full Access] Regarding '{query}': This would search QA and HR documents."
        return f"[DEMO MODE - QA Only] Regarding '{query}': This would search QA documents only."
    
    # Get available modes
    modes = search_module.check_available_modes()
    qa_available = modes["qa"]["available"]
    hr_available = modes["hr"]["available"]
    
    context_docs = []
    
    try:
        if logged_in:
            if qa_available and hr_available:
                qa_results = search_module.search(query, mode="qa", k=5)
                hr_results = search_module.search(query, mode="hr", k=5)
                combined = pd.concat([qa_results, hr_results], ignore_index=True)
                combined = combined.sort_values("cosine_similarity", ascending=False).head(10)
                context_docs = list(combined['text'].values)
            elif qa_available:
                context_docs = list(search_module.search(query, mode="qa", k=10)['text'].values)
            elif hr_available:
                context_docs = list(search_module.search(query, mode="hr", k=10)['text'].values)
        else:
            if qa_available:
                context_docs = list(search_module.search(query, mode="qa", k=10)['text'].values)
    except Exception as e:
        st.warning(f"⚠️ Search error: {e}")
    
    # Build prompt
    if context_docs:
        context = "\n\n".join(context_docs)
        prompt = f"Contexto:\n{context}\n\nPregunta: {query}\nRespuesta:"
    else:
        expert_type = "QA y HR" if logged_in else "QA"
        prompt = f"No hay documentos indexados. Responde como experto en {expert_type}.\n\nPregunta: {query}\nRespuesta:"
    
    # Prepare messages for Claude
    system_message = ""
    messages = []
    
    for msg in conversation:
        if msg["role"] == "system":
            system_message = msg["content"]
        else:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": prompt})
    
    return llm.chat(messages, system=system_message)


def process_message(message: str) -> str:
    """Process a user message."""
    logged_in = auth.is_logged_in()
    username = auth.get_current_username()
    
    # Handle Excel commands
    if is_excel_command(message):
        if logged_in and username:
            return handle_excel_command(message, username)
        return "ℹ️ Excel editing requires login."
    
    # Regular chat with RAG
    ensure_system_message(auth.get_system_prompt())
    conversation = get_conversation_history()
    
    return answer_question(message, conversation, logged_in)
