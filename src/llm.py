"""
LLM client management - Claude for chat, OpenAI for embeddings.
"""
from anthropic import Anthropic
from openai import OpenAI
from . import config

# Global clients (lazy initialized)
_claude_client = None
_openai_client = None
_mock_mode = None


def _init_clients():
    """Initialize clients on first use."""
    global _claude_client, _openai_client, _mock_mode
    
    if _mock_mode is not None:
        return  # Already initialized
    
    _mock_mode = False
    
    # Initialize Claude
    if config.ANTHROPIC_API_KEY:
        try:
            _claude_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            print("✅ Claude client configured")
        except Exception as e:
            print(f"❌ Claude error: {e}")
            _mock_mode = True
    else:
        print("⚠️ Missing ANTHROPIC_API_KEY - using mock mode")
        _mock_mode = True
    
    # Initialize OpenAI
    if config.OPENAI_API_KEY:
        try:
            _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            print("✅ OpenAI client configured (embeddings)")
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            _mock_mode = True
    else:
        print("⚠️ Missing OPENAI_API_KEY - using mock mode")
        _mock_mode = True


def get_claude_client():
    """Get Claude client for chat."""
    _init_clients()
    return _claude_client


def get_openai_client():
    """Get OpenAI client for embeddings."""
    _init_clients()
    return _openai_client


def is_mock_mode() -> bool:
    """Check if running in mock mode."""
    _init_clients()
    return _mock_mode


def chat(messages: list, system: str = "") -> str:
    """
    Send a chat request to Claude.
    
    Args:
        messages: List of {"role": "user/assistant", "content": "..."} dicts
        system: System prompt
        
    Returns:
        Assistant's response text
    """
    if is_mock_mode():
        return "[DEMO MODE] This is a simulated response."
    
    response = _claude_client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=4096,
        system=system,
        messages=messages
    )
    return response.content[0].text


def get_embedding(text: str):
    """Get embedding vector for text."""
    import numpy as np
    import faiss
    
    if is_mock_mode():
        emb = np.random.rand(1536).astype('float32')
        emb = np.ascontiguousarray(emb.reshape(1, -1))
        faiss.normalize_L2(emb)
        return emb
    
    response = _openai_client.embeddings.create(
        input=[text],
        model=config.OPENAI_EMBEDDING_MODEL
    )
    emb = np.array(response.data[0].embedding, dtype="float32")
    emb = np.ascontiguousarray(emb.reshape(1, -1))
    faiss.normalize_L2(emb)
    return emb


def get_embeddings_batch(texts: list) -> list:
    """Get embeddings for multiple texts."""
    import numpy as np
    
    if is_mock_mode():
        return [np.random.rand(1536).astype('float32').tolist() for _ in texts]
    
    response = _openai_client.embeddings.create(
        input=texts,
        model=config.OPENAI_EMBEDDING_MODEL
    )
    return [d.embedding for d in response.data]
