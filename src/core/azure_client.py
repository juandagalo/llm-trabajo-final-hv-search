"""
Azure OpenAI client management.
Centralized Azure OpenAI client configuration and management.
"""
from openai import AzureOpenAI
from ..config.settings import Config


class AzureClientManager:
    """Manages Azure OpenAI client configuration and access."""
    
    def __init__(self):
        """Initialize the Azure client manager."""
        self._client = None
        self._mock_mode = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client."""
        try:
            if not Config.validate_azure_config():
                print("⚠️  Incomplete Azure OpenAI configuration. Using mock mode.")
                self._mock_mode = True
                return
                
            self._client = AzureOpenAI(
                api_key=Config.AZURE_API_KEY,
                api_version=Config.AZURE_API_VERSION,
                azure_endpoint=Config.AZURE_ENDPOINT
            )
            print("✅ Azure OpenAI client configured successfully.")
            self._mock_mode = False
            
        except Exception as e:
            print(f"❌ Error configuring Azure OpenAI client: {e}")
            print("   Running in mock mode.")
            self._client = None
            self._mock_mode = True
    
    def get_client(self):
        """Get the Azure OpenAI client."""
        return self._client
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self._mock_mode
    
    def get_embedding_deployment(self) -> str:
        """Get the embedding deployment name."""
        return Config.AZURE_EMBEDDING_DEPLOYMENT
    
    def get_chat_model(self) -> str:
        """Get the chat model name."""
        return Config.AZURE_CHAT_MODEL


# Global singleton instance
_azure_manager = None


def get_azure_manager() -> AzureClientManager:
    """Get the global Azure client manager instance."""
    global _azure_manager
    if _azure_manager is None:
        _azure_manager = AzureClientManager()
    return _azure_manager


def get_azure_client():
    """Get the Azure OpenAI client."""
    return get_azure_manager().get_client()


def is_mock_mode() -> bool:
    """Check if running in mock mode."""
    return get_azure_manager().is_mock_mode()


def get_embedding_deployment() -> str:
    """Get the embedding deployment name."""
    return get_azure_manager().get_embedding_deployment()


def get_chat_model() -> str:
    """Get the chat model name."""
    return get_azure_manager().get_chat_model()