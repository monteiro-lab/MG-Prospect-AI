import os
import httpx

async def send_prospect_email(to_email: str, subject: str, html_content: str, from_name: str = "Mendonça Galvão Contadores") -> dict:
    """
    Integração com a API REST v3 do Brevo para envio de e-mails transacionais.
    Retorna: {"success": bool, "message_id": str | None, "error": str | None}
    """
    api_key = os.getenv("BREVO_API_KEY")
    from_email = os.getenv("BREVO_FROM_EMAIL", "contato@mondoncagalvao.com.br")

    if not api_key:
        print("AVISO: BREVO_API_KEY não configurada no .env")
        return {"success": False, "message_id": None, "error": "BREVO_API_KEY não configurada no .env"}

    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {"email": to_email}
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
            if response.status_code in [200, 201, 202]:
                data = response.json()
                msg_id = data.get("messageId")
                print(f"✅ E-mail enviado com sucesso via API Brevo para {to_email}")
                return {"success": True, "message_id": msg_id, "error": None}
            else:
                error_msg = response.text
                print(f"❌ Erro da API do Brevo: {error_msg}")
                return {"success": False, "message_id": None, "error": error_msg}
    except Exception as e:
        print(f"❌ Erro de conexão com o Brevo: {e}")
        return {"success": False, "message_id": None, "error": str(e)}