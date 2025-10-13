from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def setup_llm():
    """
    Configura e retorna o modelo LLM do Groq.
    
    Returns:
        ChatGroq: Instância configurada do modelo LLM
    """
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)
    return llm
