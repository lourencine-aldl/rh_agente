import base64
import os
import streamlit as st
import json
import time
from streamlit_extras.switch_page_button import switch_page
import streamlit.components.v1 as components
from backend import process_cv, validate_file, get_sample_data

_ROOT = os.path.dirname(os.path.abspath(__file__))
_ALDL_LOGO = os.path.join(_ROOT, "data", "aldl_logo.png")

# --- Configuração da página ---
st.set_page_config(
    page_title="ALDL · Avaliação de Currículos",
    page_icon=_ALDL_LOGO if os.path.isfile(_ALDL_LOGO) else "📋",
    layout="wide",
    initial_sidebar_state="expanded",
)



# --- Funções de processamento ---
def process_document(file_content, filename, cargo, requisitos):
    """
    Processa um documento usando o backend LangGraph.
    
    Parâmetros:
    file_content (bytes): Conteúdo do arquivo.
    filename (str): Nome do arquivo.
    cargo (str): Nome do cargo.
    requisitos (str): Descrição dos requisitos.

    Retorna:
    dict: Dados processados do currículo.
    """
    # Valida o arquivo primeiro
    validation = validate_file(file_content, filename)
    if not validation["valid"]:
        st.error(validation["message"])
        return None
    
    # Mostra indicador de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Validando arquivo...")
        progress_bar.progress(20)
        
        status_text.text("Extraindo conteúdo...")
        progress_bar.progress(40)
        
        status_text.text("Processando com IA...")
        progress_bar.progress(60)
        
        status_text.text("Analisando candidato...")
        progress_bar.progress(80)
        
        # Processa o documento
        result = process_cv(file_content, filename, cargo, requisitos)
        
        if result.get("status") == "erro":
            st.error(f"Erro no processamento: {result.get('error', 'Erro desconhecido')}")
            return None
        
        status_text.text("Finalizando...")
        progress_bar.progress(100)
        
        status_text.text("Processamento concluído!")
        time.sleep(1)
        
        # Limpa os indicadores
        progress_bar.empty()
        status_text.empty()
        
        return result
        
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        return None

def display_results(data):
    """
    Exibe os dados processados em um formato amigável.
    """
    if not data:
        return
    
    # Informações do candidato
    st.subheader("📋 Informações do Candidato", divider='gray')
    
    dados = data.get('dados_estruturados', {})
    col1, col2 = st.columns(2)
    
    with col1:
        if dados.get('nome'):
            st.info(f"**Nome:** {dados['nome']}")
        if dados.get('email'):
            st.info(f"**Email:** {dados['email']}")
        if dados.get('telefone'):
            st.info(f"**Telefone:** {dados['telefone']}")
        if dados.get('endereco'):
            st.info(f"**Endereço:** {dados['endereco']}")
        
    with col2:
        if dados.get('linkedin'):
            st.info(f"**LinkedIn:** {dados['linkedin']}")
        if dados.get('summary'):
            st.success("**Resumo:**")
            st.write(dados['summary'])
    
    # Análise da candidatura
    analise = data.get('analise', {})
    if analise:
        st.subheader("🎯 Análise da Candidatura", divider='gray')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score_raw = analise.get('score', 0)
            # Converte para inteiro, tratando casos onde pode vir como string
            try:
                score = int(score_raw) if isinstance(score_raw, (str, int, float)) else 0
            except (ValueError, TypeError):
                score = 0
            
            if score >= 70:
                st.success(f"**Pontuação:** {score}/100")
            elif score >= 50:
                st.warning(f"**Pontuação:** {score}/100")
            else:
                st.error(f"**Pontuação:** {score}/100")
        
        with col2:
            selected_raw = analise.get('selected', False)
            # Converte para boolean, tratando casos onde pode vir como string
            if isinstance(selected_raw, str):
                selected = selected_raw.lower() in ['true', '1', 'yes', 'sim', 'selecionado']
            else:
                selected = bool(selected_raw)
            
            if selected:
                st.success("**Status:** ✅ Selecionado")
            else:
                st.error("**Status:** ❌ Não selecionado")
        
        with col3:
            matching_skills = analise.get('matching_skills', [])
            st.info(f"**Habilidades correspondentes:** {len(matching_skills)}")
        
        # Feedback detalhado
        if analise.get('feedback'):
            st.subheader("💬 Feedback")
            st.write(analise['feedback'])
        
        # Habilidades
        col1, col2 = st.columns(2)
        
        with col1:
            if analise.get('matching_skills'):
                st.success("**✅ Habilidades que correspondem:**")
                for skill in analise['matching_skills']:
                    st.write(f"• {skill}")
        
        with col2:
            if analise.get('missing_skills'):
                st.warning("**⚠️ Habilidades em falta:**")
                for skill in analise['missing_skills']:
                    st.write(f"• {skill}")
    
    # Email gerado
    if data.get('email'):
        st.subheader("📧 Email Gerado", divider='gray')
        st.text_area("Conteúdo do email:", data['email'], height=150)
    
    # Detalhes da entrevista
    entrevista = data.get('entrevista', {})
    if entrevista:
        st.subheader("📅 Detalhes da Entrevista", divider='gray')
        if entrevista.get('note') and not entrevista.get('meeting_time'):
            st.info(entrevista['note'])
        else:
            col1, col2 = st.columns(2)
            with col1:
                if entrevista.get('meeting_time'):
                    st.info(f"**Data/Hora:** {entrevista['meeting_time']}")
                if entrevista.get('timezone'):
                    st.info(f"**Fuso horário:** {entrevista['timezone']}")
            with col2:
                if entrevista.get('meeting_link'):
                    st.info(f"**Link da reunião:** {entrevista['meeting_link']}")
            if entrevista.get('note'):
                st.caption(entrevista['note'])
    
    # Currículo revisado
    if data.get('curriculo_revisado'):
        with st.expander("📄 Ver currículo revisado"):
            st.text(data['curriculo_revisado'])


# --- Função para configurar a barra lateral ---
def side_navbar():
    """
    Configura a barra lateral da aplicação Streamlit.
    """
    if os.path.isfile(_ALDL_LOGO):
        with open(_ALDL_LOGO, "rb") as _lf:
            _logo_b64 = base64.standard_b64encode(_lf.read()).decode("ascii")
        st.sidebar.markdown(
            f"""
            <div style="display:flex;justify-content:center;align-items:center;width:100%;margin:0 0 6px 0;">
              <img src="data:image/png;base64,{_logo_b64}"
                   alt="ALDL"
                   style="max-width:100px;width:auto;height:auto;object-fit:contain;display:block;
                          border-radius:12px;padding:10px 14px;
                          background:linear-gradient(165deg,#ffffff 0%,#f1f5f9 100%);
                          box-shadow:0 1px 10px rgba(15,23,42,0.06);
                          border:1px solid rgba(148,163,184,0.16);
                          box-sizing:content-box;"/>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<p style="text-align:center;font-weight:800;color:#1e3a5f;font-size:1.5rem;">ALDL</p>',
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(
        "<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(100,116,139,.35),transparent);"
        "margin:10px 0 14px 0;'></div>",
        unsafe_allow_html=True,
    )

    st.sidebar.info(
        """Olá, seja bem-vindo!

Eu sou um Agente especializado em avaliação de currículos, desenvolvido para auxiliar na análise."""
    )
    
    st.sidebar.markdown("### 📋 Como usar:")
    st.sidebar.markdown("""
    1. Preencha o nome do cargo e os requisitos
    2. Clique em OK para liberar o upload
    3. Faça upload do currículo em PDF ou DOCX
    4. Aguarde a análise completa com IA
    5. Veja a avaliação detalhada
    """)
    
    st.sidebar.markdown("### ⚠️ Avisos:")
    st.sidebar.warning("""
    - Certifique-se de que o CV é válido
    - O processamento pode levar alguns minutos
    - O texto do currículo é enviado ao modelo (Groq) para análise
    - Formatos suportados: PDF e DOCX
    """)
    
    st.sidebar.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    
    if st.sidebar.button("🗑️ Limpar histórico", use_container_width=True, key="clear_history"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.write("**ALDL** · agente de avaliação de currículos")

# Configurar a barra lateral
side_navbar()


# --- Interface principal ---
st.title("🔗 AI Agent - Avaliação de Currículos")
st.markdown("### Analise currículos de candidatos a vagas com inteligência artificial")
st.markdown("---")

# Inicializar variáveis de sessão
if "ok" not in st.session_state:
    st.session_state.ok = False
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

# Formulário de configuração
with st.container():
    st.subheader("⚙️ Configuração da Vaga")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        vaga = st.text_area("Nome do cargo", placeholder="Ex: Engenheiro de IA", key="cargo_input")
    
    with col2:
        requisitos = st.text_area("Descrição dos requisitos da vaga", 
                                placeholder="Ex: Conhecimento em Python, Machine Learning, etc.", 
                                key="requisitos_input")

# Botão para processar
if not st.session_state.ok:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Configurar Vaga", type="primary", use_container_width=True, key="configure_job"):
            if vaga and requisitos:
                st.session_state.ok = True
                st.session_state.cargo = vaga
                st.session_state.requisitos = requisitos
                st.success("Configurações salvas. Agora você pode fazer o upload do currículo.")
                st.rerun()
            else:
                st.warning("Por favor, preencha o nome do cargo e os requisitos.")

# Upload e processamento
if st.session_state.ok:
    st.subheader("📄 Upload do Currículo")
    
    # Mostrar configurações atuais
    st.info(f"**Cargo:** {st.session_state.cargo}")
    st.info(f"**Requisitos:** {st.session_state.requisitos}")
    
    uploaded_file = st.file_uploader(
        "Faça upload do currículo em PDF ou DOCX", 
        type=["pdf", "docx"],
        help="Formatos suportados: PDF e DOCX (máximo 10MB)"
    )
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        
        # Botão para processar
        if st.button("🚀 Processar Currículo", type="primary", use_container_width=True, key="process_cv"):
            with st.spinner("Processando currículo..."):
                processed_data = process_document(
                    file_bytes, 
                    uploaded_file.name, 
                    st.session_state.cargo, 
                    st.session_state.requisitos
                )
                
                if processed_data:
                    st.session_state.processed_data = processed_data
                    st.success("Documento processado com sucesso!")
                    st.rerun()
    
    # Botão para resetar
    if st.button("🔄 Nova Análise", use_container_width=True, key="reset_upload"):
        st.session_state.ok = False
        st.session_state.processed_data = None
        st.rerun()

# Exibir resultados
if st.session_state.processed_data:
    st.markdown("---")
    display_results(st.session_state.processed_data)
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Copiar Email", use_container_width=True, key="copy_email"):
            email_content = st.session_state.processed_data.get('email', '')
            st.code(email_content, language=None)
    
    with col2:
        if st.button("📄 Baixar Relatório", use_container_width=True, key="download_report"):
            # Aqui você pode implementar a funcionalidade de download
            st.info("Funcionalidade de download em desenvolvimento")
    
    with col3:
        if st.button("🔄 Nova Análise", use_container_width=True, key="reset_results"):
            st.session_state.ok = False
            st.session_state.processed_data = None
            st.rerun()
        
