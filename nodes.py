from typing import Dict, Any
import json
from datetime import datetime, timedelta
import pytz
from constants import RecruitamentState
from job_description import requisitos
from llm_config import setup_llm


def analyze_cv(state: RecruitamentState) -> Dict:
    """
    Node que analisa o currículo do candidato em relação aos requisitos da vaga.
    
    Args:
        state: Estado atual do workflow contendo informações do candidato
        
    Returns:
        Dict com o resultado da análise incluindo score, feedback e habilidades
    """
    try:
        job_requirements = requisitos.get(state['cargo'], "Requisitos não encontrados")
        
        prompt = f"""Analise este curriculo em relação aos seguintes requisitos: 
        Cargo: {state['cargo']}
        Requisitos: {job_requirements}
        Currículo do candidato: {state['curriculo_text']}
        
        Forneça uma análise em formato JSON com:

        {{
            "selected": true/false,
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
        response = llm.invoke(prompt)
        content = response.content
        
        # Extrai JSON da resposta
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0].strip()
        else:
            json_str = content.strip()
            
        analysis = json.loads(json_str)
        
        # Validação e conversão de tipos
        if 'score' in analysis:
            try:
                analysis['score'] = int(analysis['score'])
            except (ValueError, TypeError):
                analysis['score'] = 0
        
        if 'selected' in analysis:
            if isinstance(analysis['selected'], str):
                analysis['selected'] = analysis['selected'].lower() in ['true', '1', 'yes', 'sim']
            else:
                analysis['selected'] = bool(analysis['selected'])
        
        return {"analysis_result": analysis}
        
    except Exception as e:
        return {"error": str(e)}


def candidate_email_generator(state: RecruitamentState) -> Dict:
    """
    Node que gera email personalizado para o candidato baseado na análise.
    
    Args:
        state: Estado atual do workflow contendo resultado da análise
        
    Returns:
        Dict com o conteúdo do email gerado
    """
    try:
        analysis = state.get('analysis_result', {})
        selected = analysis.get('selected', False)
        feedback = analysis.get('feedback', '')
        
        prompt = f"""Escreva um email de {'aprovação' if selected else 'rejeitado'} para o candidato {state['candidate_email']} com feedback específico.

        Feedback: {feedback}
        O e-mail deve ser formal e construtivo"""

        response = setup_llm().invoke(prompt)
        return {"email_content": response.content}
        
    except Exception as e:
        return {"error": str(e)}


def interview_scheduler(state: RecruitamentState) -> Dict:
    """
    Node que agenda entrevista para candidatos selecionados.
    
    Args:
        state: Estado atual do workflow
        
    Returns:
        Dict com detalhes da entrevista agendada
    """
    try:
        # Agenda entrevista para o próximo dia útil às 11h
        interview_time = (datetime.now(pytz.timezone('America/Sao_Paulo')) + timedelta(days=1)).replace(hour=11, minute=0)
        
        return {"interview_details": {
            "meeting_time": interview_time.strftime('%d/%m/%Y %H:%M'),
            "timezone": "BRT",
            "meeting_link": f"https://meeting.link/{state['thread_id']}"
        }}
        
    except Exception as e:
        return {"error": str(e)}
