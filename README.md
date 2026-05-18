# MG Prospect AI

A platform for automated B2B lead prospecting and CRM management, built for Mendonça Galvão Contadores Associados. The system uses the Google Places API to discover and score potential clients, then manages the entire sales pipeline from initial contact through email automation and status tracking.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [LGPD Compliance](#lgpd-compliance)
- [n8n Automation Integration](#n8n-automation-integration)
- [Database](#database)

---

## Architecture Overview

The project is split into two independent services that communicate over HTTP.

```
mg-prospect-frontend/    React + Vite SPA (port 5173 in development)
mg-prospect-backend/     FastAPI async REST API (port 8000 in development)
```

The frontend is a Single Page Application (SPA) that authenticates via JWT and communicates exclusively with the backend API. The backend handles all business logic, database interaction (PostgreSQL via SQLAlchemy async), email delivery (Brevo), and webhook dispatching to external automation platforms (n8n).

```
                        +-------------------+
                        |   React Frontend  |
                        |   (Vite / TSX)    |
                        +--------+----------+
                                 |
                          HTTP / REST
                                 |
                        +--------v----------+
                        |   FastAPI Backend |
                        +---+----------+----+
                            |          |
               +------------+          +------------+
               |                                    |
       +-------v-------+                  +---------v------+
       |  PostgreSQL    |                  |   External APIs |
       |  (SQLAlchemy) |                  |   Google Places |
       +---------------+                  |   Brevo (email) |
                                          |   n8n (webhook) |
                                          +-----------------+
```

---

## Technology Stack

### Backend

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.x (async) |
| Database | PostgreSQL |
| Migrations | Alembic |
| Auth | JWT (via python-jose) |
| Email | Brevo (Sendinblue API) |
| Settings | Pydantic Settings |
| Server | Uvicorn |

### Frontend

| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript |
| Build Tool | Vite |
| Routing | React Router v6 |
| HTTP Client | Axios |
| Maps | MapLibre GL / react-map-gl |
| Icons | Lucide React |
| Styling | Vanilla CSS (custom design system) |

---

## Project Structure

```
MG Prospect AI/
├── N8N_WORKFLOW_README.md        # n8n automation workflow guide
│
├── mg-prospect-backend/
│   ├── alembic/                  # Database migration files
│   ├── app/
│   │   ├── auth/                 # JWT authentication, user model
│   │   ├── campaigns/            # Campaign creation and execution
│   │   ├── core/                 # Config, database session, dependencies
│   │   ├── crm/                  # CRM status and pipeline management
│   │   ├── emails/               # Email templates, rendering, Brevo dispatch
│   │   ├── integrations/         # Google Places API client
│   │   ├── leads/                # Lead model, scoring, CRUD
│   │   ├── public/               # Unauthenticated routes (interest form, unsubscribe)
│   │   └── main.py               # FastAPI app entrypoint, CORS, router registry
│   ├── .env                      # Environment variables (not committed)
│   └── requirements.txt
│
└── mg-prospect-frontend/
    ├── src/
    │   ├── components/
    │   │   ├── LeadDetails.tsx    # Lead detail drawer with mini-map
    │   │   ├── Layout.tsx         # Authenticated layout shell
    │   │   └── CampaignSearchLogs.tsx
    │   ├── pages/
    │   │   ├── Dashboard.tsx      # Metrics overview
    │   │   ├── Leads.tsx          # Lead list + Radar map mode
    │   │   ├── Campaigns.tsx      # Campaign management
    │   │   ├── CRM.tsx            # Sales pipeline / Kanban
    │   │   ├── Templates.tsx      # Email template editor
    │   │   ├── InterestForm.tsx   # Public lead interest capture page
    │   │   ├── Unsubscribe.tsx    # LGPD opt-out confirmation page
    │   │   ├── Login.tsx
    │   │   └── ResetPassword.tsx
    │   ├── services/
    │   │   └── api.ts             # Axios instance with JWT interceptor
    │   └── App.tsx                # Router with public/private route split
    ├── index.html
    └── vite.config.ts
```

---

## Features

### Automated Lead Prospecting
Campaigns are configured with a keyword, target city, and state. The backend queries the Google Places Text Search API to discover businesses matching the criteria, enriches each result with details (phone, website, rating, coordinates) via the Places Details API, deduplicates against existing records, and calculates a composite lead score.

### Lead Scoring
Each lead receives a score from 0 to 100 based on weighted signals: presence of email, phone, website, Google rating, number of reviews, and business operational status.

### CRM Pipeline
Leads move through a customizable status pipeline (NOVO, PROSPECTADO, EM NEGOCIACAO, INTERESSADO, CLIENTE, NAO INTERESSADO). The Dashboard tracks conversion rates between stages.

### Email Automation
Email templates support variable interpolation for lead-specific fields (`{nome_empresa}`, `{cidade}`, `{link_formulario_interesse}`, etc.). All outbound emails include a personalized unsubscribe link in the footer. The dispatch engine blocks sending to any lead with the `do_not_contact` flag set.

### Radar Map Mode
The Leads page offers a toggle between a standard table view and a Radar mode: an interactive full-screen map (MapLibre GL) where each lead is plotted as a live marker with a category-specific icon. Supports three map styles (Carto Dark, OpenStreetMap, OpenStreetMap 3D). Clicking a marker opens the lead detail drawer. Filtering by campaign isolates markers to a single prospecting area.

### Lead Detail Mini-Map
When a lead has geographic coordinates (latitude/longitude, captured from Google Places), a contextual mini-map is rendered inside the lead detail panel, centered on the business location with a dark-themed style.

### Public Interest Form
A branded, unauthenticated page (`/interesse/:token`) allows leads to voluntarily submit their contact data. The form includes real-time Brazilian phone number masking (`(XX) XXXXX-XXXX`). On submission, the data is saved and a webhook fires to n8n for downstream automation.

### LGPD Opt-Out
A dedicated unsubscribe endpoint (`POST /api/v1/public/unsubscribe/:token`) sets the `do_not_contact` flag on the lead record. The frontend renders a confirmation page at `/unsubscribe/:token` that calls this endpoint automatically on load.

---

## Environment Variables

Create a `.env` file in `mg-prospect-backend/` with the following keys:

```env
# Core
SECRET_KEY=your-very-long-secret-key-here
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mg_prospect

# Google Places API (required for campaign prospecting)
GOOGLE_PLACES_API_KEY=your-google-places-api-key

# Brevo (Sendinblue) for email dispatch
BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=contato@mendoncagalvao.com.br
BREVO_SENDER_NAME=Mendonca Galvao Contadores Associados

# Frontend URL (used for CORS and generating unsubscribe links in emails)
FRONTEND_URL=http://localhost:5173

# n8n Webhook (optional, enables automated follow-up on lead interest)
N8N_WEBHOOK_LEAD_INTEREST_URL=https://your-n8n-instance.com/webhook/interesse
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
cd mg-prospect-backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive documentation is at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd mg-prospect-frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## API Reference

All authenticated routes require a `Bearer` token in the `Authorization` header obtained from `POST /api/v1/auth/login`.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Obtain JWT access token |
| POST | `/api/v1/auth/reset-password` | Reset user password |

### Leads

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/leads` | List leads with filtering and pagination |
| POST | `/api/v1/leads` | Create a lead manually |
| GET | `/api/v1/leads/{id}` | Get a single lead |
| PUT | `/api/v1/leads/{id}` | Update lead data or status |
| DELETE | `/api/v1/leads/{id}` | Delete a lead |

Query parameters for `GET /api/v1/leads`: `page`, `page_size`, `search`, `status`, `city`, `state`, `category`, `campaign_id`, `has_email`, `min_score`, `sort_by`, `sort_order`.

### Campaigns

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/campaigns` | List all campaigns |
| POST | `/api/v1/campaigns` | Create and start a campaign |
| GET | `/api/v1/campaigns/{id}` | Get campaign details and metrics |
| GET | `/api/v1/campaigns/{id}/logs` | Get real-time execution logs |

### Emails

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/emails/templates` | List email templates |
| POST | `/api/v1/emails/templates` | Create email template |
| PUT | `/api/v1/emails/templates/{id}` | Update email template |
| DELETE | `/api/v1/emails/templates/{id}` | Delete email template |
| POST | `/api/v1/emails/preview` | Preview rendered email for a lead |
| POST | `/api/v1/emails/send` | Send email to a single lead |

### Public (No Authentication Required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/public/interest/:token` | Fetch lead data for interest form pre-fill |
| POST | `/api/v1/public/interest/:token` | Submit interest form data |
| POST | `/api/v1/public/unsubscribe/:token` | Set `do_not_contact` flag (LGPD opt-out) |

---

## LGPD Compliance

The platform was designed with the Lei Geral de Proteção de Dados (LGPD) in mind:

1. **Explicit Consent:** The public interest form includes a mandatory consent checkbox. The payload forwarded to n8n includes the `consent` boolean so downstream automations can gate active outreach.

2. **Opt-Out Mechanism:** Every outbound email includes a unique unsubscribe link in the footer, generated from the lead's `public_token`. Clicking the link calls `POST /api/v1/public/unsubscribe/:token`, setting `do_not_contact = True` on the lead record.

3. **Send-Time Enforcement:** The email dispatch engine checks `do_not_contact` before every send. If the flag is set, the request is rejected with HTTP 400 regardless of who initiates it.

---

## n8n Automation Integration

When a lead submits the interest form, the backend fires a webhook to the URL configured in `N8N_WEBHOOK_LEAD_INTEREST_URL`. The webhook dispatch is non-blocking (runs as a background task) so the lead's confirmation screen is not delayed by network latency.

For the full workflow architecture including Redis memory keys and AI follow-up loop, see [N8N_WORKFLOW_README.md](./N8N_WORKFLOW_README.md).

### Webhook Payload

```json
{
  "event": "lead_interest_created",
  "source": "mg_prospect_ai",
  "lead": {
    "id": 123,
    "public_token": "a1b2c3d4e5f6g7h8",
    "company_name": "Farmacia Extra Popular",
    "segment": "Farmacia",
    "city": "Petrolina",
    "state": "PE",
    "phone": "(87) 3864-0024",
    "email": "contato@empresa.com"
  },
  "interest": {
    "id": 456,
    "contact_name": "Joao Silva",
    "email": "joao@email.com",
    "phone": "87999999999",
    "preferred_contact_time": "Manha",
    "message": "Tenho interesse em conversar",
    "consent": true,
    "created_at": "2026-05-15T10:00:00.000Z"
  }
}
```

---

## Database

Schema management is handled by Alembic. After any change to SQLAlchemy models:

```bash
# Generate a new migration
alembic revision --autogenerate -m "describe the change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

Key tables: `users`, `leads`, `campaigns`, `campaign_logs`, `lead_interests`, `email_templates`.

The `leads` table stores Google Places data including `latitude` and `longitude`, which powers the Radar Map and the mini-map in the lead detail panel.
