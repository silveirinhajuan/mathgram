import streamlit as st
from datetime import datetime
from database import create_post, get_posts, toggle_like, user_liked_post, get_comments, create_comment
from latex_utils import render_latex, export_to_tex, escape_html

def show_create_post():
    """Exibe interface para criar novo post."""
    st.subheader("Criar Novo Post")
    
    # Inicializa variáveis no session_state se não existirem
    if 'last_post_data' not in st.session_state:
        st.session_state.last_post_data = None
    
    with st.form("create_post_form"):
        title = st.text_input("Título do Post", max_chars=200)
        content = st.text_area(
            "Conteúdo (LaTeX suportado)", 
            height=200,
            help="Use $...$ para matemática inline, $$...$$ ou \\[...\\] para display math. Suporta química com \\ce{}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            show_preview = st.checkbox("Mostrar Preview", value=False)
        with col2:
            submit_post = st.form_submit_button("Publicar Post")
        
        # Preview dentro do form
        if show_preview and content:
            st.subheader("Preview:")
            with st.container():
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                render_latex(content, f"preview-{hash(content)}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Submissão
        if submit_post:
            user = st.session_state.user
            success, message = create_post(
                user['id'], 
                user['email'], 
                user['name'], 
                title, 
                content
            )
            
            if success:
                st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                # Armazena dados do post para exportação
                st.session_state.last_post_data = {
                    'title': title,
                    'content': content,
                    'author': user['name']
                }
                st.info("Post publicado! Vá para a aba Feed para ver.")
            else:
                st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
    
    # Botão de exportar fora do form
    if st.session_state.last_post_data:
        st.subheader("Exportar Último Post")
        post_data = st.session_state.last_post_data
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📥 Exportar como .tex"):
                tex_content = export_to_tex(
                    post_data['title'], 
                    post_data['content'], 
                    post_data['author']
                )
                safe_title = post_data['title'].replace(' ', '_').replace('/', '_')
                filename = safe_title + '.tex'
                st.download_button(
                    label="Download .tex",
                    data=tex_content,
                    file_name=filename,
                    mime="text/plain",
                    key="download_tex"
                )

def show_feed():
    """Exibe feed de posts."""
    st.subheader("Feed")
    
    posts = get_posts()
    
    if not posts:
        st.info("Nenhum post ainda. Seja o primeiro a postar!")
        return
    
    for post in posts:
        # Container do post
        with st.container():
            st.markdown('<div class="post-card">', unsafe_allow_html=True)
            
            # Header do post
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                st.markdown(f'<img src="{post["avatar_url"]}" class="avatar">', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="post-title">{escape_html(post["title"])}</div>', unsafe_allow_html=True)
                post_date = datetime.strptime(post['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y às %H:%M')
                st.markdown(f'<div class="post-meta">Por {escape_html(post["author_name"])} • {post_date}</div>', unsafe_allow_html=True)
            
            with col3:
                # Botão de like
                user_liked = user_liked_post(post['id'], st.session_state.user['id'])
                like_icon = "❤️" if user_liked else "🤍"
                if st.button(f"{like_icon} {post['likes']}", key=f"like_{post['id']}"):
                    if toggle_like(post['id'], st.session_state.user['id']):
                        st.rerun()
            
            # Conteúdo do post
            st.markdown("**Conteúdo:**")
            render_latex(post['content'], f"post-{post['id']}")
            
            # Seção de comentários
            st.markdown('<div class="comment-section">', unsafe_allow_html=True)
            
            # Formulário para novo comentário
            with st.expander(f"💬 Comentários ({len(get_comments(post['id']))})"):
                comment_content = st.text_area(
                    "Adicionar comentário:",
                    key=f"comment_{post['id']}",
                    height=80
                )
                
                if st.button("Comentar", key=f"submit_comment_{post['id']}"):
                    if comment_content.strip():
                        user = st.session_state.user
                        success, message = create_comment(
                            post['id'],
                            user['id'],
                            user['email'],
                            user['name'],
                            comment_content
                        )
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Comentário não pode estar vazio.")
                
                # Mostrar comentários existentes
                comments = get_comments(post['id'])
                for comment in comments:
                    st.markdown(f'''
                    <div class="comment">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <img src="{comment["avatar_url"]}" style="width: 24px; height: 24px; border-radius: 50%; margin-right: 8px;">
                            <strong>{escape_html(comment["author_name"])}</strong>
                            <span style="color: #666; margin-left: 8px; font-size: 0.8rem;">
                                {datetime.strptime(comment["created_at"], '%Y-%m-%d %H:%M:%S').strftime('%d/%m às %H:%M')}
                            </span>
                        </div>
                        <div>{escape_html(comment["content"])}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Separador
            st.markdown("---")

def show_main_app():
    """Exibe interface principal do aplicativo."""
    # Header com logout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        user_name = st.session_state.user['name']
        st.write(f"👋 Olá, **{user_name}**!")
    with col2:
        st.markdown('<h1 class="main-header">📐 Mathgram</h1>', unsafe_allow_html=True)
    with col3:
        if st.button("Sair", key="logout"):
            del st.session_state.user
            st.rerun()
    
    # Navegação
    tab1, tab2 = st.tabs(["📝 Novo Post", "🏠 Feed"])
    
    with tab1:
        show_create_post()
    
    with tab2:
        show_feed()