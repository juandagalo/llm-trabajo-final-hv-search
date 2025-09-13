
import os
from openai import AzureOpenAI
from recuperacion_consulta_faiss import search
from dotenv import load_dotenv

# Cargar configuración desde .env
load_dotenv()
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
ENDPOINT = os.getenv("ENDPOINT")
MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL", "gpt-4.1-nano")

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)


def answer_question(query: str, conversation_history: list) -> str:
    """
    Dada una pregunta, busca contexto relevante y genera una respuesta usando Azure OpenAI.
    conversation_history debe ser una lista de mensajes (dicts) gestionada externamente (por ejemplo, en session_state).
    """
    res = search(query)
    results = list(res['text'].values)
    context = "\n\n".join(results)
    prompt = f"Contexto:\n{context}\n\nPregunta: {query}\nRespuesta:"
    conversation_history.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=MODEL,
        messages=conversation_history
    )
    assistant_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply