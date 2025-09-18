"""
Configuración centralizada del cliente Azure OpenAI para todo el proyecto.
"""
import os
from openai import AzureOpenAI
from dotenv import load_dotenv


class AzureClientConfig:
    """Configuración centralizada para el cliente Azure OpenAI."""
    
    def __init__(self):
        """Inicializa la configuración cargando variables de entorno."""
        load_dotenv()
        self.endpoint = os.getenv("ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.embedding_deployment = os.getenv("DEPLOYMENT")
        self.chat_model = os.getenv("AZURE_OPENAI_CHAT_MODEL", "gpt-4.1-nano")
        
        # Verificar configuración
        self._validate_config()
        
        # Inicializar cliente
        self.client = self._create_client()
        self.mock_mode = self.client is None
    
    def _validate_config(self):
        """Valida que las variables de entorno necesarias estén configuradas."""
        required_vars = {
            "ENDPOINT": self.endpoint,
            "AZURE_OPENAI_API_KEY": self.api_key,
            "AZURE_OPENAI_API_VERSION": self.api_version,
            "DEPLOYMENT": self.embedding_deployment
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            print(f"⚠️  Advertencia: Variables de entorno faltantes: {missing_vars}")
            print("   El sistema funcionará en modo demo/mock.")
    
    def _create_client(self):
        """Crea y retorna el cliente Azure OpenAI."""
        try:
            if not all([self.endpoint, self.api_key, self.api_version]):
                print("⚠️  Configuración incompleta de Azure OpenAI. Usando modo mock.")
                return None
                
            client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            print("✅ Cliente Azure OpenAI configurado correctamente.")
            return client
            
        except Exception as e:
            print(f"❌ Error configurando cliente Azure OpenAI: {e}")
            print("   El sistema funcionará en modo demo/mock.")
            return None
    
    def get_client(self):
        """Retorna el cliente Azure OpenAI."""
        return self.client
    
    def is_mock_mode(self):
        """Retorna True si está en modo mock/demo."""
        return self.mock_mode
    
    def get_embedding_deployment(self):
        """Retorna el nombre del deployment para embeddings."""
        return self.embedding_deployment
    
    def get_chat_model(self):
        """Retorna el nombre del modelo para chat."""
        return self.chat_model
    
    def get_config_dict(self):
        """Retorna un diccionario con la configuración para compatibilidad."""
        return {
            'endpoint': self.endpoint,
            'deployment': self.embedding_deployment,
            'api_key': self.api_key,
            'api_version': self.api_version
        }


# Instancia global singleton
_azure_config = None


def get_azure_config():
    """
    Retorna la configuración global de Azure OpenAI (singleton).
    
    Returns:
        AzureClientConfig: Instancia de configuración
    """
    global _azure_config
    if _azure_config is None:
        _azure_config = AzureClientConfig()
    return _azure_config


def get_azure_client():
    """
    Retorna el cliente Azure OpenAI configurado.
    
    Returns:
        AzureOpenAI or None: Cliente configurado o None si está en modo mock
    """
    return get_azure_config().get_client()


def is_mock_mode():
    """
    Indica si el sistema está en modo mock/demo.
    
    Returns:
        bool: True si está en modo mock
    """
    return get_azure_config().is_mock_mode()


def get_embedding_deployment():
    """
    Retorna el nombre del deployment para embeddings.
    
    Returns:
        str: Nombre del deployment
    """
    return get_azure_config().get_embedding_deployment()


def get_chat_model():
    """
    Retorna el nombre del modelo para chat.
    
    Returns:
        str: Nombre del modelo
    """
    return get_azure_config().get_chat_model()