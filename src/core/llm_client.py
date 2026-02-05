"""
LLM client management.
Centralized Claude (for chat) and OpenAI (for embeddings) client configuration.
"""
from anthropic import Anthropic
from openai import OpenAI
from ..config.settings import Config


class LLMClientManager:
    """Manages Claude and OpenAI client configuration and access."""
    
    def __init__(self):
        """Initialize the LLM client manager."""
        self._claude_client = None
        self._openai_client = None
        self._mock_mode = False
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize the Claude and OpenAI clients."""
        try:
            # Check Claude configuration
            if not Config.validate_claude_config():
                print("⚠️  Missing ANTHROPIC_API_KEY. Using mock mode for chat.")
                self._mock_mode = True
            else:
                self._claude_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                print("✅ Claude client configured successfully.")
            
            # Check OpenAI configuration for embeddings
            if not Config.validate_openai_config():
                print("⚠️  Missing OPENAI_API_KEY. Using mock mode for embeddings.")
                self._mock_mode = True
            else:
                self._openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("✅ OpenAI client configured successfully (for embeddings).")
            
            if self._claude_client and self._openai_client:
                self._mock_mode = False
                
        except Exception as e:
            print(f"❌ Error configuring LLM clients: {e}")
            print("   Running in mock mode.")
            self._claude_client = None
            self._openai_client = None
            self._mock_mode = True
    
    def get_claude_client(self):
        """Get the Claude (Anthropic) client for chat."""
        return self._claude_client
    
    def get_openai_client(self):
        """Get the OpenAI client for embeddings."""
        return self._openai_client
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self._mock_mode
    
    def get_embedding_model(self) -> str:
        """Get the embedding model name."""
        return Config.OPENAI_EMBEDDING_MODEL
    
    def get_chat_model(self) -> str:
        """Get the Claude chat model name."""
        return Config.CLAUDE_MODEL


# Global singleton instance
_llm_manager = None


def get_llm_manager() -> LLMClientManager:
    """Get the global LLM client manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMClientManager()
    return _llm_manager


def get_claude_client():
    """Get the Claude client for chat."""
    return get_llm_manager().get_claude_client()


def get_openai_client():
    """Get the OpenAI client for embeddings."""
    return get_llm_manager().get_openai_client()


def is_mock_mode() -> bool:
    """Check if running in mock mode."""
    return get_llm_manager().is_mock_mode()


def get_embedding_model() -> str:
    """Get the embedding model name."""
    return get_llm_manager().get_embedding_model()


def get_chat_model() -> str:
    """Get the chat model name."""
    return get_llm_manager().get_chat_model()
