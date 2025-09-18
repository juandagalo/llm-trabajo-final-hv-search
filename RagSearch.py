
from recuperacion_consulta_faiss import search
from azure_client import get_azure_client, get_chat_model, is_mock_mode


def answer_question(query: str, conversation_history: list, mode: str = "hr") -> str:
    """
    Dada una pregunta, busca contexto relevante y genera una respuesta usando Azure OpenAI.
    conversation_history debe ser una lista de mensajes (dicts) gestionada externamente (por ejemplo, en session_state).
    mode: "hr" for Human Resources, "qa" for QA Testing - determines search strategy and context.
    """
    if is_mock_mode():
        # Return a mock response based on mode for demo purposes
        mode_responses = {
            "hr": f"[DEMO MODE] Based on HR knowledge, regarding '{query}': This would be a response about human resources topics, including hiring, performance management, employee relations, and workplace policies. The system would normally search through HR documents to provide specific answers.",
            "qa": f"[DEMO MODE] Based on QA testing expertise, regarding '{query}': This would be a response about software testing, quality assurance methodologies, test automation, bug tracking, and testing best practices. The system would normally search through QA testing documents to provide specific answers."
        }
        assistant_reply = mode_responses.get(mode, mode_responses["hr"])
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply
    
    res = search(query, mode=mode)
    results = list(res['text'].values)
    context = "\n\n".join(results)
    
    # Adjust prompt based on mode
    if mode == "qa":
        prompt = f"Contexto:\n{context}\n\nPregunta relacionada con testing: {query}\nRespuesta:"
    else:
        prompt = f"Contexto:\n{context}\n\nPregunta: {query}\nRespuesta:"
    
    conversation_history.append({"role": "user", "content": prompt})
    
    client = get_azure_client()
    model = get_chat_model()
    
    response = client.chat.completions.create(
        model=model,
        messages=conversation_history
    )
    assistant_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply