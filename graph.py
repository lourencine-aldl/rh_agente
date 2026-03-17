from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END
from typing import Dict
import uuid
from constants import RecruitamentState
from nodes import analyze_cv, candidate_email_generator, interview_scheduler
from llm_config import setup_llm


def extract_content(file_path: str) -> str:
    """Extrai texto de todas as páginas do PDF."""
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    parts = [doc.page_content for doc in pages if doc.page_content and doc.page_content.strip()]
    return "\n\n".join(parts) if parts else ""


def analyze_agent(texto: str) -> str:
    llm = setup_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Você é um assistente de RH que extrai as informações de um currículo, remove formatações erradas, "
            "como espaços em branco, quebras de linha, etc. Não faça comentários ou tentativas de colocar em "
            "formatação como negrito, retorne APENAS o texto corrigido.",
        ),
        ("user", "Extraia os dados do curriculo e melhore sua formatação.\nCurrículo:\n{texto}"),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"texto": texto})


def structured_agent(texto: str) -> dict:
    """Extrai campos estruturados do currículo (JSON)."""
    llm = setup_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Você é um assistente de RH que extrai informações chaves de um candidato através de um texto não estruturado. "
            "Responda apenas com JSON válido.",
        ),
        (
            "user",
            """Extraia os dados do curriculo e retorne um JSON com as chaves exatamente:
    - nome
    - email
    - telefone
    - endereco (rua, cidade ou estado)
    - summary (resumo profissional)
    - linkedin

    Currículo:
    {texto}""",
        ),
    ])
    chain = prompt | llm | JsonOutputParser()
    return chain.invoke({"texto": texto})


# Alias para compatibilidade com código/notebooks antigos
sctructured_agent = structured_agent


# Workflow LangGraph
workflow = StateGraph(RecruitamentState)
workflow.add_node("analyze_cv", analyze_cv)
workflow.add_node("candidate_email_generator", candidate_email_generator)
workflow.add_node("interview_scheduler", interview_scheduler)
workflow.set_entry_point("analyze_cv")
workflow.add_edge("analyze_cv", "candidate_email_generator")
workflow.add_edge("candidate_email_generator", "interview_scheduler")
workflow.add_edge("interview_scheduler", END)

graph = workflow.compile()


def create_initial_state(
    curriculo_text: str,
    cargo: str,
    candidate_email: str,
    requisitos_vaga: str,
) -> Dict:
    """Cria o estado inicial para o workflow de recrutamento."""
    return {
        "thread_id": str(uuid.uuid4()),
        "curriculo_text": curriculo_text,
        "cargo": cargo,
        "candidate_email": candidate_email,
        "requisitos_vaga": (requisitos_vaga or "").strip(),
        "analysis_result": {},
        "interview_result": {},
        "email_content": "",
        "error": None,
    }
