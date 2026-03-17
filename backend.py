import os
import tempfile
from typing import Dict, Any

from docx import Document
import streamlit as st
from graph import graph, create_initial_state, analyze_agent, structured_agent, extract_content


def normalize_dados_estruturados(raw: Any) -> Dict[str, Any]:
    """Alinha chaves vindas do LLM (Nome, email, etc.) ao que o frontend espera."""
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, Any] = {}
    for k, v in raw.items():
        if v is None or (isinstance(v, str) and not v.strip()):
            continue
        key = str(k).strip().lower().replace(" ", "_")
        if key in ("nome", "name", "nome_completo"):
            out.setdefault("nome", v)
        elif key in ("email", "e-mail"):
            out.setdefault("email", v)
        elif key in ("telefone", "phone", "tel"):
            out.setdefault("telefone", v)
        elif "endereco" in key or key in ("address", "cidade", "localização", "rua"):
            out.setdefault("endereco", v)
        elif key in ("summary", "resumo", "resumo_profissional"):
            out.setdefault("summary", v)
        elif "linkedin" in key:
            out.setdefault("linkedin", v)
    return out


def process_cv(file_content: bytes, filename: str, cargo: str, requisitos: str) -> Dict[str, Any]:
    """
    Processa um currículo e retorna a análise completa.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        try:
            if filename.lower().endswith(".pdf"):
                curriculo_text = extract_content(tmp_file_path)
            elif filename.lower().endswith(".docx"):
                curriculo_text = extract_docx_content(tmp_file_path)
            else:
                return {
                    "error": "Formato de arquivo não suportado. Use PDF ou DOCX.",
                    "status": "erro",
                }

            if not (curriculo_text or "").strip():
                return {
                    "error": "Não foi possível extrair texto do arquivo (pode estar vazio ou ser imagem escaneada).",
                    "status": "erro",
                }

            curriculo_revisado = analyze_agent(curriculo_text)
            raw_estruturado = structured_agent(curriculo_revisado)
            dados_estruturados = normalize_dados_estruturados(raw_estruturado)

            email_candidato = (
                dados_estruturados.get("email")
                or "candidato@email.nao.identificado"
            )

            initial_state = create_initial_state(
                curriculo_text=curriculo_revisado,
                cargo=cargo or "Vaga",
                candidate_email=email_candidato,
                requisitos_vaga=requisitos or "",
            )

            result = graph.invoke(
                input=initial_state,
                config={"configurable": {"thread_id": initial_state["thread_id"]}},
            )

            return {
                "dados_estruturados": dados_estruturados,
                "analise": result.get("analysis_result", {}),
                "email": result.get("email_content", ""),
                "entrevista": result.get("interview_result") or {},
                "curriculo_revisado": curriculo_revisado,
                "status": "sucesso",
            }

        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except Exception as e:
        return {"error": f"Erro ao processar o currículo: {str(e)}", "status": "erro"}


def extract_docx_content(file_path: str) -> str:
    """Extrai texto dos parágrafos do DOCX."""
    try:
        doc = Document(file_path)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(lines)
    except Exception as e:
        raise Exception(f"Erro ao extrair conteúdo do DOCX: {str(e)}") from e


def validate_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    if len(file_content) == 0:
        return {"valid": False, "message": "O arquivo está vazio."}

    allowed_extensions = [".pdf", ".docx"]
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return {
            "valid": False,
            "message": f"Formato não suportado. Use: {', '.join(allowed_extensions)}",
        }

    max_size = 10 * 1024 * 1024
    if len(file_content) > max_size:
        return {"valid": False, "message": "Arquivo muito grande. Máximo permitido: 10MB"}

    return {"valid": True, "message": "Arquivo válido para processamento."}


@st.cache_data
def get_sample_data():
    return {
        "dados_estruturados": {
            "nome": "João da Silva",
            "email": "joao.silva@exemplo.com",
            "telefone": "+55 11 99876-5432",
            "endereco": "São Paulo, SP",
            "summary": "Desenvolvedor Python com 5 anos de experiência.",
            "linkedin": "https://linkedin.com/in/joaosilva",
        },
        "analise": {
            "selected": True,
            "feedback": "Candidato qualificado.",
            "matching_skills": ["Python", "Machine Learning"],
            "missing_skills": ["TensorFlow"],
            "score": 85,
        },
        "email": "Prezado João,\n\n...",
        "entrevista": {
            "meeting_time": "15/01/2024 11:00",
            "timezone": "BRT",
            "meeting_link": "https://meet.placeholder/12345",
        },
        "curriculo_revisado": "João da Silva\n...",
        "status": "sucesso",
    }
