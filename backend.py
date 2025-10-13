import os
import tempfile
from typing import Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader
from docx import Document
import streamlit as st
from graph import graph, create_initial_state, analyze_agent, sctructured_agent, extract_content
from constants import ExtractResume

def process_cv(file_content: bytes, filename: str, cargo: str, requisitos: str) -> Dict[str, Any]:
    """
    Processa um currículo e retorna a análise completa.
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome do arquivo
        cargo: Nome do cargo para o qual o candidato está se candidatando
        requisitos: Descrição dos requisitos da vaga
        
    Returns:
        Dict com os resultados da análise
    """
    try:
        # Salva o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extrai o conteúdo do arquivo
            if filename.lower().endswith('.pdf'):
                curriculo_text = extract_content(tmp_file_path)
            elif filename.lower().endswith('.docx'):
                curriculo_text = extract_docx_content(tmp_file_path)
            else:
                return {"error": "Formato de arquivo não suportado. Use PDF ou DOCX."}
            
            # Processa o currículo com IA para melhorar formatação
            curriculo_revisado = analyze_agent(curriculo_text)
            
            # Extrai informações estruturadas
            dados_estruturados = sctructured_agent(curriculo_revisado)
            
            # Cria estado inicial para o workflow
            initial_state = create_initial_state(
                curriculo_text=curriculo_revisado,
                cargo=cargo,
                candidate_email=dados_estruturados.get('email', 'email@exemplo.com')
            )
            
            # Atualiza os requisitos no estado
            initial_state['requisitos'] = requisitos
            
            # Executa o workflow completo
            result = graph.invoke(
                input=initial_state, 
                config={"configurable": {"thread_id": initial_state["thread_id"]}}
            )
            
            # Combina os resultados
            resultado_final = {
                "dados_estruturados": dados_estruturados,
                "analise": result.get("analysis_result", {}),
                "email": result.get("email_content", ""),
                "entrevista": result.get("interview_result", {}),
                "curriculo_revisado": curriculo_revisado,
                "status": "sucesso"
            }
            
            return resultado_final
            
        finally:
            # Remove o arquivo temporário
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        return {"error": f"Erro ao processar o currículo: {str(e)}", "status": "erro"}

def extract_docx_content(file_path: str) -> str:
    """
    Extrai o conteúdo de um arquivo DOCX.
    
    Args:
        file_path: Caminho para o arquivo DOCX
        
    Returns:
        String com o conteúdo do documento
    """
    try:
        doc = Document(file_path)
        text_content = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text.strip())
        
        return "\n".join(text_content)
    except Exception as e:
        raise Exception(f"Erro ao extrair conteúdo do DOCX: {str(e)}")

def validate_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Valida se o arquivo é válido para processamento.
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome do arquivo
        
    Returns:
        Dict com status da validação
    """
    # Verifica se o arquivo não está vazio
    if len(file_content) == 0:
        return {"valid": False, "message": "O arquivo está vazio."}
    
    # Verifica o formato do arquivo
    allowed_extensions = ['.pdf', '.docx']
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        return {"valid": False, "message": f"Formato não suportado. Use: {', '.join(allowed_extensions)}"}
    
    # Verifica o tamanho do arquivo (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_content) > max_size:
        return {"valid": False, "message": "Arquivo muito grande. Máximo permitido: 10MB"}
    
    return {"valid": True, "message": "Arquivo válido para processamento."}

@st.cache_data
def get_sample_data():
    """
    Retorna dados de exemplo para demonstração.
    
    Returns:
        Dict com dados de exemplo
    """
    return {
        "dados_estruturados": {
            "nome": "João da Silva",
            "email": "joao.silva@exemplo.com",
            "telefone": "+55 11 99876-5432",
            "endereco": "São Paulo, SP",
            "summary": "Desenvolvedor Python com 5 anos de experiência em desenvolvimento de software e análise de dados.",
            "linkedin": "https://linkedin.com/in/joaosilva"
        },
        "analise": {
            "selected": True,
            "feedback": "Candidato altamente qualificado com experiência sólida em Python e tecnologias relacionadas.",
            "matching_skills": ["Python", "Machine Learning", "Data Analysis", "SQL"],
            "missing_skills": ["TensorFlow", "Cloud Computing"],
            "score": 85
        },
        "email": "Prezado João,\n\nAgradecemos seu interesse na vaga de Engenheiro de IA. Após análise do seu currículo, ficamos impressionados com sua experiência em Python e Machine Learning.\n\nGostaríamos de agendar uma entrevista para discutir melhor sua candidatura.\n\nAtenciosamente,\nEquipe de RH",
        "entrevista": {
            "meeting_time": "15/01/2024 11:00",
            "timezone": "BRT",
            "meeting_link": "https://meeting.link/12345"
        },
        "curriculo_revisado": "João da Silva\nDesenvolvedor Python Sênior\n\nExperiência: 5 anos em desenvolvimento de software\nHabilidades: Python, Machine Learning, Data Analysis\nEducação: Bacharelado em Ciência da Computação",
        "status": "sucesso"
    }
