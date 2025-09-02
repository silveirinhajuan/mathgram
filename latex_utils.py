import streamlit.components.v1 as components
from datetime import datetime

def escape_html(text: str) -> str:
    """Escapa caracteres HTML para prevenir injeção."""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))

def render_latex(content: str, element_id: str = "math-content") -> None:
    """Renderiza conteúdo LaTeX usando KaTeX."""
    # Escapa o conteúdo para prevenir injeção de HTML/JS
    safe_content = escape_html(content)
    
    # HTML com KaTeX
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css">
        <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.js"></script>
        <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/contrib/auto-render.min.js"></script>
        <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/contrib/mhchem.min.js"></script>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 10px;
                background: #0e1117;
                color: #fafafa;
            }}
            
            /* Força sempre modo escuro para melhor compatibilidade */
            .katex {{
                color: #fafafa !important;
            }}
            
            .katex .base {{
                color: #fafafa !important;
            }}
            
            .katex .mord,
            .katex .mop,
            .katex .mrel,
            .katex .mbin,
            .katex .mpunct,
            .katex .mopen,
            .katex .mclose {{
                color: #fafafa !important;
            }}
            
            /* Força texto sempre branco para matemática */
            .katex * {{
                color: #fafafa !important;
            }}
            
            #math-content {{
                word-wrap: break-word;
                overflow-wrap: break-word;
                color: #fafafa;
            }}
        </style>
    </head>
    <body>
        <div id="{element_id}">{safe_content}</div>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                // Força sempre modo escuro para melhor renderização
                document.body.style.background = '#0e1117';
                document.body.style.color = '#fafafa';
                
                renderMathInElement(document.getElementById('{element_id}'), {{
                    delimiters: [
                        {{left: '$$', right: '$$', display: true}},
                        {{left: '\\[', right: '\\]', display: true}},
                        {{left: '$', right: '$', display: false}},
                        {{left: '\\(', right: '\\)', display: false}}
                    ],
                    throwOnError: false,
                    trust: true,
                    macros: {{
                        "\\\\ce": "\\\\ce"
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_content, height=None, scrolling=True)

def export_to_tex(title: str, content: str, author: str) -> str:
    """Gera conteúdo LaTeX para exportação."""
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    # Escapa caracteres especiais para LaTeX
    safe_title = escape_html(title)
    safe_author = escape_html(author)
    
    tex_content = "\\documentclass{article}\n"
    tex_content += "\\usepackage[utf8]{inputenc}\n"
    tex_content += "\\usepackage[T1]{fontenc}\n"
    tex_content += "\\usepackage{amsmath}\n"
    tex_content += "\\usepackage{amsfonts}\n"
    tex_content += "\\usepackage{amssymb}\n"
    tex_content += "\\usepackage{mhchem}\n"
    tex_content += "\\usepackage[portuguese]{babel}\n\n"
    tex_content += f"\\title{{{safe_title}}}\n"
    tex_content += f"\\author{{{safe_author}}}\n"
    tex_content += f"\\date{{{current_date}}}\n\n"
    tex_content += "\\begin{document}\n\n"
    tex_content += "\\maketitle\n\n"
    tex_content += content + "\n\n"
    tex_content += "\\end{document}\n"
    
    return tex_content