"""
LLM principal: Groq. Fallback automático para OpenAI se Groq falhar
(limite de taxa, indisponibilidade, erro de autenticação, etc.),
desde que OPENAI_API_KEY esteja definida no .env.
"""
import logging
import os

from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

_GROQ_MODEL = "openai/gpt-oss-120b"
_OPENAI_MODEL = "gpt-4o-mini"

_groq_client = None
_openai_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = ChatGroq(model=_GROQ_MODEL, temperature=0.7)
    return _groq_client


def _get_openai():
    global _openai_client
    if _openai_client is None:
        key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if key:
            _openai_client = ChatOpenAI(
                model=_OPENAI_MODEL,
                temperature=0.7,
                api_key=key,
            )
    return _openai_client


def _invoke_with_fallback(input, config=None):
    groq = _get_groq()
    openai = _get_openai()
    try:
        return groq.invoke(input, config=config)
    except Exception as e:
        if openai is None:
            logger.error("Groq falhou e não há OPENAI_API_KEY para fallback: %s", e)
            raise
        logger.warning(
            "Groq indisponível ou erro (%s). A usar OpenAI (%s).",
            type(e).__name__,
            _OPENAI_MODEL,
        )
        return openai.invoke(input, config=config)


def setup_llm():
    """
    Retorna um Runnable compatível com chains LangChain (prompt | llm | parser).
    Tenta Groq primeiro; em falha, OpenAI se a chave existir.
    """
    return RunnableLambda(_invoke_with_fallback)
