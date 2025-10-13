from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END
import os
from typing import Dict
import uuid
from constants import ExtractResume, ReviewResume, RecruitamentState
from job_description import requisitos
from nodes import analyze_cv, candidate_email_generator, interview_scheduler
from llm_config import setup_llm

def extract_content(file_path) -> str: 
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    for text in pages:
        texto = text.page_content
        return texto


def analyze_agent(texto: str) -> str:
    llm = setup_llm()

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de RH que extrai as informações de um currículo, remove formatações erradas, como espaços em branco, quebras de linha, etc. Não faça comentários ou tentativas de colocar em formatação como negrito, retorne APENAS o texto corrigido "),
    ("user", """Extraia os dados do curriculo e melhore sua formatação.
    Currículo: {texto}"""),
])

    parser = StrOutputParser()

    chain = prompt | llm | parser
    # Get the response from the model
    response = chain.invoke(texto)
    
    return response

def sctructured_agent(texto: str) -> str:
    # Initialize the Groq model
    llm = setup_llm()

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de RH que extrai informações chaves de um candidato através de um texto não estruturado."),
    ("user", """Extraia os dados do curriculo e retorne um JSON com as seguintes chaves:
    - Nome
    - email
    - telefone
    - Rua, endereço/cidade ou estado
    - resumo
    - linkedin.
    Currículo: {texto}"""),
])

    parser = JsonOutputParser()

    chain = prompt | llm | parser
    # Get the response from the model
    response = chain.invoke(texto)
    
    return response


# Configuração do Workflow LangGraph
workflow = StateGraph(RecruitamentState)
workflow.add_node("analyze_cv",analyze_cv)
workflow.add_node("candidate_email_generator",candidate_email_generator)
workflow.add_node("interview_scheduler", interview_scheduler)
workflow.set_entry_point("analyze_cv")
workflow.add_edge("analyze_cv", "candidate_email_generator")
workflow.add_edge("candidate_email_generator", "interview_scheduler")
workflow.add_edge("interview_scheduler", END)

# Compila o workflow
graph = workflow.compile()


def create_initial_state(curriculo_text: str, cargo: str, candidate_email: str) -> Dict:
    """Cria o estado inicial para o workflow de recrutamento"""
    return {
        "thread_id": str(uuid.uuid4()),
        "curriculo_text": curriculo_text,
        "cargo": cargo,
        "candidate_email": candidate_email,
        "analysis_result": {},
        "interview_result": {},
        "email_content": "",
        "error": None
    }
