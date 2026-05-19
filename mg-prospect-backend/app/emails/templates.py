from typing import Dict, Any
import os
import re
from app.core.config import settings
from app.emails.logo_b64 import LOGO_BASE64

def get_frontend_url():
    return os.getenv("FRONTEND_URL", "http://localhost:5173")

def render_email_template(template_content: str, lead_data: Dict[str, Any]) -> str:
    """
    Substitui as variáveis do template pelos dados reais do lead.
    Adiciona suporte para {nome_empresa}, {cidade}, {estado}, {segmento}, etc.
    """
    if not template_content:
        return ""

    public_token = lead_data.get("public_token") or "demo-token"
    frontend_url = get_frontend_url().rstrip('/')
    link_formulario = f"{frontend_url}/interesse/{public_token}"
    unsubscribe_url = f"{frontend_url}/unsubscribe/{public_token}"

    mapping = {
        "{nome_empresa}": lead_data.get("name") or "Empresa",
        "{cidade}": lead_data.get("city") or "sua região",
        "{estado}": lead_data.get("state") or "",
        "{segmento}": lead_data.get("category") or "sua área de atuação",
        "{telefone}": lead_data.get("phone") or "Não informado",
        "{website}": lead_data.get("website") or "Não informado",
        "{link_instagram}": "https://www.instagram.com/mendoncagalvaoo/",
        "{link_formulario_interesse}": link_formulario,
        "{link_whatsapp}": "https://wa.me/5587999999999",
        "{unsubscribe_url}": unsubscribe_url
    }
    
    rendered_text = template_content
    for key, value in mapping.items():
        rendered_text = rendered_text.replace(key, str(value))
        
    return rendered_text

def format_email_html(rendered_body: str, public_token: str) -> str:
    """
    Envolve o texto renderizado em um HTML premium estruturado com as cores da Mendonça Galvão.
    Inclui a logo real da empresa no header.
    Branco/off-white no corpo, preto/grafite nos textos, e detalhes dourados.
    """
    # Processar o conteúdo: separar blocos HTML existentes de texto puro
    rendered_body = rendered_body.replace("\r\n", "\n").replace("\r", "\n")

    html_block_pattern = re.compile(r'(<div[\s\S]*?</div>|<p[\s\S]*?</p>)', re.IGNORECASE)
    parts = html_block_pattern.split(rendered_body)

    processed_parts = []
    for part in parts:
        # Se é um bloco HTML, preservar como está
        if re.match(r'^<(div|p)\s', part, re.IGNORECASE):
            processed_parts.append(part)
            continue

        # Se é texto puro, converter \n\n em parágrafos e \n em <br>
        paragraphs = [p for p in part.split("\n\n") if p.strip()]
        if not paragraphs:
            continue

        for para in paragraphs:
            lines = para.split("\n")
            bullet_lines = [l for l in lines if l.strip().startswith("•")]

            if len(bullet_lines) > 1:
                # É uma lista — separar título dos itens
                title_lines = [l for l in lines if not l.strip().startswith("•") and l.strip()]
                items = "".join(f"<li>{l.strip()[1:].strip()}</li>" for l in bullet_lines)
                if title_lines:
                    processed_parts.append(f"<p>{'<br>'.join(l.strip() for l in title_lines)}</p>")
                processed_parts.append(f"<ul>{items}</ul>")
            else:
                # Parágrafo normal
                processed_parts.append(f"<p>{para.replace(chr(10), '<br>')}</p>")

    rendered_body = "".join(processed_parts)

    unsubscribe_url = f"{settings.FRONTEND_URL}/unsubscribe/{public_token}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:5173/unsubscribe/{public_token}"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mendonça Galvão Contadores Associados</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #F8F9FA;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2D3748;
                -webkit-font-smoothing: antialiased;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #FFFFFF;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border-top: 4px solid #D4AF37;
            }}
            .header {{
                text-align: center;
                padding: 30px 20px;
                background-color: #1A202C;
            }}
            .header img {{
                max-width: 180px;
                height: auto;
            }}
            .content {{
                padding: 40px 35px;
                font-size: 15px;
                line-height: 1.8;
                color: #4A5568;
                text-align: justify;
            }}
            .content p {{
                margin: 0 0 18px 0;
            }}
            .content ul {{
                margin: 8px 0 20px 0;
                padding-left: 24px;
                list-style: none;
            }}
            .content ul li {{
                padding: 6px 0;
                position: relative;
            }}
            .content ul li::before {{
                content: '\\2022';
                color: #D4AF37;
                font-weight: bold;
                font-size: 18px;
                position: absolute;
                left: -18px;
                top: 4px;
            }}
            .cta-container {{
                text-align: center;
                margin: 30px 0;
            }}
            .cta-button {{
                display: inline-block;
                background-color: #D4AF37;
                color: #1A202C !important;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                letter-spacing: 0.3px;
            }}
            .divider {{
                height: 1px;
                background: linear-gradient(to right, transparent, #D4AF37, transparent);
                margin: 28px 0;
            }}
            .footer {{
                background-color: #F1F5F9;
                padding: 24px 30px;
                text-align: center;
                font-size: 12px;
                color: #718096;
            }}
            .footer a {{
                color: #D4AF37;
                text-decoration: none;
            }}
            .footer p {{
                margin: 6px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{LOGO_BASE64}" alt="Mendonça Galvão Contadores Associados" style="max-width: 180px; height: auto;" />
            </div>
            <div class="content">
                {rendered_body}
            </div>
            <div class="footer">
                <p>Mendonça Galvão Contadores Associados<br>Petrolina - PE</p>
                <p>Contato institucional enviado para apresentação de serviços contábeis.</p>
                <p>Caso não queira receber novos contatos, <a href="{unsubscribe_url}">clique aqui para descadastrar</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template