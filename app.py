import streamlit as st
from auth import show_auth_page
from main_app import show_main_app
from database import init_database

# ================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ================================

# Configuração da página
st.set_page_config(
    page_title="Mathgram",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Força tema escuro para melhor renderização do LaTeX
st.markdown("""
<script>
    // Força tema escuro no Streamlit
    const theme = window.parent.document.querySelector('[data-theme]');
    if (theme) {
        theme.setAttribute('data-theme', 'dark');
    }
</script>
""", unsafe_allow_html=True)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .post-card {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }
    
    .post-meta {
        color: #666;
        font-size: 0.9rem;
    }
    
    .post-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin: 0.5rem 0;
        color: var(--text-color);
    }
    
    .like-button {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.2rem;
    }
    
    .comment-section {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }
    
    .comment {
        background: var(--secondary-background-color);
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 3px solid #1f77b4;
    }
    
    .error-message {
        color: #ff4444;
        background: #ffe6e6;
        padding: 0.8rem;
        border-radius: 5px;
        border-left: 4px solid #ff4444;
    }
    
    .success-message {
        color: #00aa00;
        background: #e6ffe6;
        padding: 0.8rem;
        border-radius: 5px;
        border-left: 4px solid #00aa00;
    }
    
    .preview-box {
        border: 1px solid var(--border-color);
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        background: var(--background-color);
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# APLICAÇÃO PRINCIPAL
# ================================

def main():
    """Função principal da aplicação."""
    # Inicializa banco de dados
    init_database()
    
    # Inicializa session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Roteamento baseado em autenticação
    if st.session_state.user is None:
        show_auth_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()