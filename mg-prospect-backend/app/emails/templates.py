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
    # Converter as quebras de linha em parágrafos se não for HTML
    if "<p>" not in rendered_body and "<br>" not in rendered_body:
        rendered_body = "<br><br>".join(rendered_body.split("\n\n"))
        rendered_body = rendered_body.replace("\n", "<br>")

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
                padding: 40px 30px;
                font-size: 16px;
                line-height: 1.7;
                color: #4A5568;
            }}
            .content h1 {{
                color: #1A202C;
                font-size: 22px;
                margin-bottom: 20px;
            }}
            .content p {{
                margin-bottom: 16px;
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
                padding: 14px 28px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
            }}
            .divider {{
                height: 1px;
                background: linear-gradient(to right, transparent, #D4AF37, transparent);
                margin: 24px 0;
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