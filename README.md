# AI Agent - Avaliação de Currículos

Sistema de análise de currículos com inteligência artificial usando Streamlit e LangGraph.

![Sistema](https://github.com/MoisesArruda/rh_agents/blob/main/data/graph.png)

## 🚀 Funcionalidades

- **Upload de currículos** em PDF e DOCX
- **Análise automática** com IA usando Groq
- **Extração de informações** estruturadas do currículo
- **Avaliação de candidatos** baseada em requisitos da vaga
- **Geração automática de emails** de resposta
- **Agendamento de entrevistas** automático
- **Interface intuitiva** com Streamlit

## 📋 Pré-requisitos

- Python 3.8+
- Chave API do Groq

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd RH_agent
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
# Crie um arquivo .env na raiz do projeto
echo "GROQ_API_KEY=sua_chave_api_groq_aqui" > .env
```

4. Execute a aplicação:
```bash
streamlit run frontend.py
```

## 📁 Estrutura do Projeto

```
RH_agent/
├── frontend.py          # Interface principal em Streamlit
├── backend.py           # Módulo de processamento
├── graph.py             # Workflow LangGraph principal
├── nodes.py             # Nodes do workflow (análise, email, entrevista)
├── llm_config.py        # Configuração do modelo LLM
├── constants.py         # Modelos Pydantic e tipos
├── job_description.py   # Descrições de vagas
├── requirements.txt     # Dependências Python
└── data/               # Arquivos de dados
    └── ArrudaConsulting.jpeg
```

## 🔧 Como Usar

1. **Configure a vaga**: Preencha o nome do cargo e os requisitos
2. **Upload do currículo**: Faça upload de um arquivo PDF ou DOCX
3. **Processamento**: O sistema analisará automaticamente o currículo
4. **Resultados**: Visualize a análise, email gerado e detalhes da entrevista

## 🎯 Recursos da IA

- **Extração de dados**: Nome, email, telefone, endereço, LinkedIn
- **Análise de compatibilidade**: Comparação com requisitos da vaga
- **Pontuação**: Score de 0-100 baseado na adequação
- **Feedback detalhado**: Análise das habilidades e pontos de melhoria
- **Email personalizado**: Geração automática de resposta ao candidato
- **Agendamento**: Criação automática de link para entrevista

## 🔒 Segurança

- Todos os dados são processados localmente
- Arquivos temporários são removidos após processamento
- Validação de formatos e tamanhos de arquivo
- Limite de 10MB por arquivo

