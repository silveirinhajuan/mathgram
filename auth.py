import streamlit as st
import bcrypt
import sqlite3
import re
from typing import Optional, Dict, Any

def hash_password(password: str) -> str:
    """Gera hash seguro da senha usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def validate_password(password: str) -> tuple[bool, str]:
    """Valida a força da senha."""
    if len(password) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    if not re.search(r'[A-Za-z]', password):
        return False, "A senha deve conter pelo menos uma letra."
    if not re.search(r'[0-9]', password):
        return False, "A senha deve conter pelo menos um número."
    return True, "Senha válida."

def validate_email(email: str) -> bool:
    """Valida formato do email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_user(email: str, name: Optional[str], password: str) -> tuple[bool, str]:
    """Cria um novo usuário no banco de dados."""
    if not validate_email(email):
        return False, "Email inválido."
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        # Verifica se email já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email já registrado."
        
        # Cria usuário
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
            (email, name, hashed_password)
        )
        
        conn.commit()
        conn.close()
        return True, "Usuário criado com sucesso!"
        
    except Exception as e:
        return False, f"Erro ao criar usuário: {str(e)}"

def authenticate_user(email: str, password: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    """Autentica usuário e retorna dados se válido."""
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, email, name, password_hash FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[3]):
            return True, {
                'id': user[0],
                'email': user[1],
                'name': user[2] or email.split('@')[0]
            }
        else:
            return False, None
            
    except Exception as e:
        st.error(f"Erro na autenticação: {str(e)}")
        return False, None

def show_auth_page():
    """Exibe página de login/cadastro."""
    st.markdown('<h1 class="main-header">📐 Mathgram</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Rede social para conteúdos de exatas</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Cadastro"])
    
    with tab1:
        st.subheader("Entrar")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                if not email or not password:
                    st.markdown('<div class="error-message">Preencha todos os campos.</div>', unsafe_allow_html=True)
                else:
                    success, user_data = authenticate_user(email, password)
                    if success:
                        st.session_state.user = user_data
                        st.rerun()
                    else:
                        st.markdown('<div class="error-message">Email ou senha incorretos.</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Criar Conta")
        with st.form("register_form"):
            email = st.text_input("Email", key="register_email")
            name = st.text_input("Nome (opcional)", key="register_name")
            password = st.text_input("Senha", type="password", key="register_password")
            confirm_password = st.text_input("Confirmar Senha", type="password", key="confirm_password")
            submit_register = st.form_submit_button("Criar Conta")
            
            if submit_register:
                if not email or not password:
                    st.markdown('<div class="error-message">Email e senha são obrigatórios.</div>', unsafe_allow_html=True)
                elif password != confirm_password:
                    st.markdown('<div class="error-message">Senhas não coincidem.</div>', unsafe_allow_html=True)
                else:
                    success, message = create_user(email, name, password)
                    if success:
                        st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                        st.info("Agora você pode fazer login!")
                    else:
                        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)