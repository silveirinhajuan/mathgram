import sqlite3
import hashlib
from typing import List, Dict, Any

def init_database():
    """Inicializa o banco de dados SQLite com as tabelas necessárias."""
    conn = sqlite3.connect('mathgram.db')
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            author_name TEXT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Tabela de comentários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            author_name TEXT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Tabela de likes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_gravatar_url(email: str, size: int = 40) -> str:
    """Gera URL do Gravatar baseado no email."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"

def get_posts() -> List[Dict[str, Any]]:
    """Recupera todos os posts ordenados por data (mais recentes primeiro)."""
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.user_id, p.email, p.author_name, p.title, p.content, 
                   p.likes, p.created_at, COUNT(l.id) as actual_likes
            FROM posts p
            LEFT JOIN likes l ON p.id = l.post_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        ''')
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row[0],
                'user_id': row[1],
                'email': row[2],
                'author_name': row[3] or row[2].split('@')[0],
                'title': row[4],
                'content': row[5],
                'likes': row[8],  # usar actual_likes
                'created_at': row[7],
                'avatar_url': get_gravatar_url(row[2])
            })
        
        conn.close()
        return posts
        
    except Exception as e:
        print(f"Erro ao carregar posts: {str(e)}")
        return []

def create_post(user_id: int, email: str, author_name: str, title: str, content: str) -> tuple[bool, str]:
    """Cria um novo post."""
    if not title.strip():
        return False, "Título é obrigatório."
    if not content.strip():
        return False, "Conteúdo é obrigatório."
    
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO posts (user_id, email, author_name, title, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, email, author_name, title, content))
        
        conn.commit()
        conn.close()
        return True, "Post criado com sucesso!"
        
    except Exception as e:
        return False, f"Erro ao criar post: {str(e)}"

def toggle_like(post_id: int, user_id: int) -> bool:
    """Alterna o like de um post."""
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        # Verifica se já curtiu
        cursor.execute(
            "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
            (post_id, user_id)
        )
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Remove like
            cursor.execute(
                "DELETE FROM likes WHERE post_id = ? AND user_id = ?",
                (post_id, user_id)
            )
        else:
            # Adiciona like
            cursor.execute(
                "INSERT INTO likes (post_id, user_id) VALUES (?, ?)",
                (post_id, user_id)
            )
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao curtir post: {str(e)}")
        return False

def user_liked_post(post_id: int, user_id: int) -> bool:
    """Verifica se usuário já curtiu o post."""
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
            (post_id, user_id)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
        
    except Exception as e:
        return False

def get_comments(post_id: int) -> List[Dict[str, Any]]:
    """Recupera comentários de um post."""
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, email, author_name, content, created_at
            FROM comments
            WHERE post_id = ?
            ORDER BY created_at ASC
        ''', (post_id,))
        
        comments = []
        for row in cursor.fetchall():
            comments.append({
                'id': row[0],
                'user_id': row[1],
                'email': row[2],
                'author_name': row[3] or row[2].split('@')[0],
                'content': row[4],
                'created_at': row[5],
                'avatar_url': get_gravatar_url(row[2])
            })
        
        conn.close()
        return comments
        
    except Exception as e:
        print(f"Erro ao carregar comentários: {str(e)}")
        return []

def create_comment(post_id: int, user_id: int, email: str, author_name: str, content: str) -> tuple[bool, str]:
    """Cria um novo comentário."""
    if not content.strip():
        return False, "Comentário não pode estar vazio."
    
    try:
        conn = sqlite3.connect('mathgram.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments (post_id, user_id, email, author_name, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (post_id, user_id, email, author_name, content))
        
        conn.commit()
        conn.close()
        return True, "Comentário adicionado!"
        
    except Exception as e:
        return False, f"Erro ao adicionar comentário: {str(e)}"