import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def get_azure_client_and_deployment():
    """
    Carga variables de entorno y retorna el cliente AzureOpenAI y el nombre del deployment.
    Requiere las variables: ENDPOINT, DEPLOYMENT, AZURE_OPENAI_API_KEY, (opcional) AZURE_OPENAI_API_VERSION.
    """
    load_dotenv()
    endpoint = os.environ.get("ENDPOINT")
    deployment = os.environ.get("DEPLOYMENT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
    if not all([endpoint, deployment, api_key]):
        raise ValueError("Faltan variables de entorno para Azure OpenAI.")
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    return client, deployment
