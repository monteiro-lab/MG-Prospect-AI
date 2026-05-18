# Workflow Sugerido para N8N + Redis + IA (Follow-up Automatizado)

O **MG Prospect AI** agora possui integração direta via Webhook para sistemas de automação como o **n8n**. Sempre que um lead preenche a nova **Página Pública de Interesse**, o sistema envia um payload com todos os detalhes.

O objetivo desta integração é qualificar o lead sem sobrecarregar a equipe comercial humana, utilizando IA para dialogar com o lead, enquanto o Redis fornece memória stateful entre as mensagens.

## Como configurar o MG Prospect AI
Adicione no arquivo `.env` do backend:
```env
N8N_WEBHOOK_LEAD_INTEREST_URL=https://seu-n8n.com/webhook/interesse
```
Caso haja falha de conexão com o n8n, o MG Prospect AI não perderá os dados: eles serão salvos com status `new` na tabela `lead_interests` para posterior sincronização ou consulta manual.

## Exemplo de Payload Enviado
```json
{
  "event": "lead_interest_created",
  "source": "mg_prospect_ai",
  "lead": {
    "id": 123,
    "public_token": "a1b2c3d4e5f6g7h8",
    "company_name": "Farmácia Extra Popular",
    "segment": "Farmácia",
    "city": "Petrolina",
    "state": "PE",
    "phone": "(87) 3864-0024",
    "email": "contato@empresa.com"
  },
  "interest": {
    "id": 456,
    "contact_name": "João Silva",
    "email": "joao@email.com",
    "phone": "87999999999",
    "preferred_contact_time": "Manhã",
    "message": "Tenho interesse em conversar",
    "consent": true,
    "created_at": "2026-05-15T10:00:00.000Z"
  }
}
```

## Arquitetura do Workflow no n8n

1. **Webhook Trigger:** O n8n recebe o payload acima do MG Prospect AI.
2. **Validação e LGPD:** O n8n checa a propriedade `interest.consent`. Se for falso, ele não inicia nenhuma automação ativa de conversa.
3. **Gerenciamento de Memória (Redis):** O n8n deve salvar as seguintes chaves no Redis:
   - `lead:{public_token}:profile` (salvando nome da empresa, segmento, etc).
   - `lead:{public_token}:conversation` (inicializa uma string ou array JSON para o histórico da conversa).
   - `lead:{public_token}:followup_state` (Define o estágio do lead, ex: `aguardando_ia`, `qualificado`, `transbordo_humano`).
   - `lead:{public_token}:last_contact_at` (Data do último envio de mensagem).
4. **Notificação Interna:** O n8n dispara uma mensagem para o Slack, Discord ou Telegram da equipe comercial.
5. **Geração de Mensagem com IA:**
   - Lê a chave `lead:{public_token}:conversation` do Redis.
   - Usa um nó do OpenAI GPT-4 ou Anthropic Claude-3 com um "System Prompt" de SDR (Sales Development Representative) Contábil B2B.
   - Fornece o contexto e a mensagem deixada pelo lead no formulário para a IA gerar a próxima mensagem cordial.
6. **Disparo:** O n8n envia a mensagem gerada pela IA (ex: via WhatsApp Oficial API ou E-mail da Mendonça Galvão).
7. **Loop de Respostas:** Caso o lead responda a mensagem, um segundo Webhook no n8n (vinculado ao WhatsApp/E-mail) recebe a resposta, puxa novamente a memória do Redis pelo telefone/email, concatena a resposta, e re-envia para a IA. Quando a intenção é resolvida, a IA sugere o agendamento de reunião humana e o n8n muda a flag do Redis para `transbordo_humano`.
