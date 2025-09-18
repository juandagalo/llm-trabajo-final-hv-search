"""
RAG (Retrieval-Augmented Generation) functionality for answering questions.
"""
from typing import List, Dict, Any
from .search import search
from .azure_client import get_azure_client, get_chat_model, is_mock_mode


class RAGService:
    """Handles RAG operations for question answering."""
    
    def __init__(self):
        """Initialize the RAG service."""
        pass
    
    def answer_question(self, query: str, conversation_history: List[Dict[str, str]], mode: str = "hr") -> str:
        """
        Answer a question using RAG approach with conversation context.
        
        Args:
            query: User's question
            conversation_history: List of conversation messages
            mode: Search mode ('hr' or 'qa')
            
        Returns:
            Generated answer
        """
        if is_mock_mode():
            # Return mock response based on mode
            mode_responses = {
                "hr": f"[DEMO MODE] Based on HR knowledge, regarding '{query}': "
                      "This would be a response about human resources topics, including hiring, "
                      "performance management, employee relations, and workplace policies. "
                      "The system would normally search through HR documents to provide specific answers.",
                "qa": f"[DEMO MODE] Based on QA testing expertise, regarding '{query}': "
                      "This would be a response about software testing, quality assurance methodologies, "
                      "test automation, bug tracking, and testing best practices. "
                      "The system would normally search through QA testing documents to provide specific answers."
            }
            
            assistant_reply = mode_responses.get(mode, mode_responses["hr"])
            return assistant_reply
        
        # Perform document search
        search_results = search(query, mode=mode)
        context_documents = list(search_results['text'].values)
        context = "\n\n".join(context_documents)
        
        # Create mode-specific prompt
        if mode == "qa":
            prompt = (f"Contexto:\n{context}\n\n"
                     f"Pregunta: {query}\n"
                     f"Respuesta:")
        else:
            prompt = (f"Contexto:\n{context}\n\n"
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
        
        # Don't modify the original conversation_history here - let the calling function handle it
        return assistant_reply


# Global RAG service instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def answer_question(query: str, conversation_history: List[Dict[str, str]], mode: str = "hr") -> str:
    """
    Convenience function for answering questions.
    
    Args:
        query: User's question
        conversation_history: List of conversation messages
        mode: Search mode ('hr' or 'qa')
        
    Returns:
        Generated answer
    """
    return get_rag_service().answer_question(query, conversation_history, mode)