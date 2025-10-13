from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, TypedDict

class ExtractResume(BaseModel):
    nome: str = Field(description="Nome completo do candidato")
    email: Optional[str] = Field(description="Email do candidato")
    telefone: Optional[str] = Field(description="Número de telefone do candidato")
    endereco: Optional[str] = Field(description="Endereço, cidade ou estado do candidato")
    summary: str = Field(description="Resumo das principais qualificações e experiências")
    linkedin: str = Field(description="URL do perfil do LinkedIn do candidato")

class ReviewResume(BaseModel):
    resume: str = Field(description="Currículo revisado do candidato")

class RecruitamentState(TypedDict):
    """State for the recruitment process."""
    thread_id: str
    cargo: str
    curriculo_text: str
    candidate_email: str
    analysis_result: Dict[str, Any]
    interview_result: Dict[str, Any]
    email_content: str
    error: Optional[str]