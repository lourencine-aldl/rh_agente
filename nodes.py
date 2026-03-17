from typing import Dict, Any
import json
from datetime import datetime, timedelta
import pytz
from constants import RecruitamentState
from job_description import requisitos as requisitos_predefinidos
from llm_config import setup_llm


def _requisitos_para_analise(state: RecruitamentState) -> str:
    """Prioriza requisitos digitados na app; senão usa mapa de job_description."""
    texto_ui = (state.get("requisitos_vaga") or "").strip()
    if texto_ui:
        return texto_ui
    cargo = state.get("cargo", "")
    return requisitos_predefinidos.get(cargo, "Requisitos não especificados. Preencha o campo na aplicação.")


def analyze_cv(state: RecruitamentState) -> Dict[str, Any]:
    """
    Analisa o currículo face aos requisitos da vaga (texto da UI ou predefinidos).
    """
    try:
        job_requirements = _requisitos_para_analise(state)
        prompt = f"""Analise este curriculo em relação aos seguintes requisitos:
        Cargo: {state['cargo']}
        Requisitos da vaga:
        {job_requirements}

        Currículo do candidato:
        {state['curriculo_text']}

        Forneça uma análise em formato JSON com:

        {{
            "selected": true,
            "feedback": "feedback detalhado sobre o candidato",
            "matching_skills": ["habilidades que correspondem aos requisitos"],
            "missing_skills": ["habilidades que faltam ao candidato"],
            "score": 85
        }}

        IMPORTANTE:
        - "selected" deve ser true ou false (boolean)
        - "score" deve ser um número inteiro de 0 a 100
        - "matching_skills" e "missing_skills" devem ser arrays de strings
        """

        llm = setup_llm()
        content = llm.invoke(prompt).content

        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        analysis = json.loads(json_str)

        if "score" in analysis:
            try:
                analysis["score"] = int(analysis["score"])
            except (ValueError, TypeError):
                analysis["score"] = 0

        if "selected" in analysis:
            if isinstance(analysis["selected"], str):
                analysis["selected"] = analysis["selected"].lower() in ["true", "1", "yes", "sim"]
            else:
                analysis["selected"] = bool(analysis["selected"])

        return {"analysis_result": analysis}

    except Exception as e:
        return {
            "analysis_result": {
                "selected": False,
                "feedback": f"Não foi possível concluir a análise automaticamente: {e}",
                "matching_skills": [],
                "missing_skills": [],
                "score": 0,
            },
            "error": str(e),
        }


def candidate_email_generator(state: RecruitamentState) -> Dict[str, Any]:
    """Gera e-mail de resposta com base na análise."""
    try:
        analysis = state.get("analysis_result") or {}
        selected = analysis.get("selected", False)
        feedback = analysis.get("feedback", "")
        email_dest = state.get("candidate_email", "candidato")

        prompt = f"""Escreva um email de {'aprovação' if selected else 'rejeição'} para o candidato ({email_dest}) com feedback específico.

        Feedback da análise: {feedback}
        O e-mail deve ser formal, em português, e construtivo."""

        response = setup_llm().invoke(prompt)
        return {"email_content": response.content}

    except Exception as e:
        return {"email_content": f"(Erro ao gerar e-mail: {e})", "error": str(e)}


def interview_scheduler(state: RecruitamentState) -> Dict[str, Any]:
    """Sugere data/hora e link apenas para candidatos marcados como selecionados."""
    try:
        analysis = state.get("analysis_result") or {}
        if not analysis.get("selected"):
            return {
                "interview_result": {
                    "meeting_time": "",
                    "timezone": "",
                    "meeting_link": "",
                    "note": "Candidato não selecionado — sem agendamento de entrevista.",
                }
            }

        tz = pytz.timezone("America/Sao_Paulo")
        base = datetime.now(tz) + timedelta(days=1)
        interview_time = base.replace(hour=11, minute=0, second=0, microsecond=0)

        details = {
            "meeting_time": interview_time.strftime("%d/%m/%Y %H:%M"),
            "timezone": "BRT",
            "meeting_link": f"https://meet.placeholder/{state['thread_id']}",
            "note": "Substitua o link por Calendly, Google Meet ou ferramenta real de agendamento.",
        }
        return {"interview_result": details}

    except Exception as e:
        return {"interview_result": {}, "error": str(e)}
