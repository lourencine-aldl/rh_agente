# Propostas de evolução — rh_agents

## Curto prazo (já alinhado com as correções recentes)

| Proposta | Descrição |
|----------|-----------|
| **PDF escaneado** | Integrar OCR (ex.: Tesseract, ou API) para CVs só em imagem. |
| **DOCX completo** | Extrair também texto de **tabelas** e cabeçalhos/rodapés no DOCX. |
| **Grafo condicional** | Só gerar bloco “entrevista” se `selected == true`; ramo alternativo para rejeitados. |
| **Testes** | Testes unitários para `extract_content`, `normalize_dados_estruturados`, `_requisitos_para_analise`. |

## Médio prazo

- **Agendamento real**: Calendly, Google Calendar API ou Microsoft Graph em vez de link placeholder.
- **Persistência**: Base de dados ou ficheiros para histórico de candidaturas (com consentimento).
- **Multi-vaga**: Guardar modelos de vaga e reutilizar requisitos.
- **Rate limit / fila**: Evitar abuso do endpoint Groq em ambiente partilhado.
- **Observabilidade**: Logging estruturado (sem dados pessoais em claro) e métricas de latência.

## Produto / RH

- Exportar relatório em **PDF** (o botão “Baixar relatório” hoje é placeholder).
- Comparar **vários currículos** na mesma vaga (ranking).
- Checklist de **conformidade** (LGPD: base legal, retenção, anonimização).

## DevOps

- `Dockerfile` + `docker-compose` com variável `GROQ_API_KEY`.
- CI (GitHub Actions): lint + testes em push.

---

*Documento vivo — atualiza conforme prioridades do projeto.*
