# 🇲🇦 Guichet Numérique Citoyen — e-Gov Maroc Multi-Agent

> Architecture multi-agent LangGraph (Supervisor) pour la digitalisation des services publics marocains.

## 🎯 Use Case

Plateforme intelligente de traitement des demandes citoyennes couvrant :

| Agent | Rôle |
|-------|------|
| **Supervisor** | Orchestre et délègue aux agents spécialisés |
| **Triage** | Classifie la demande citoyenne (document / réclamation / guide / suivi) |
| **Document** | Traite les demandes d'actes administratifs (naissance, résidence, casier) |
| **Réclamation** | Gère les plaintes contre les administrations publiques |
| **Guide** | Oriente le citoyen dans les procédures administratives |
| **Monitoring** | Observabilité — Correlation ID, métriques, alertes |

## 🏗️ Architecture

```
                    ┌──────────────┐
                    │  FastAPI     │
                    │  /invoke     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Supervisor  │◄── Correlation ID
                    └──────┬───────┘
                           │
           ┌───────┬───────┼───────┬──────────┐
           ▼       ▼       ▼       ▼          ▼
        Triage  Document  Récl.  Guide   Monitoring
```

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- Clé API Groq (ou OpenAI)

### Installation locale

```bash
git clone https://github.com/<your-user>/egov-maroc-multi-agent.git
cd egov-maroc-multi-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # ← remplir GROQ_API_KEY
uvicorn src.main:app --reload
```

### Docker

```bash
docker compose up --build
# API disponible sur http://localhost:8000
```

### Tests

```bash
pytest tests/ -v --tb=short
```

## 📡 Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/invoke` | Soumettre une demande citoyenne |
| GET | `/health` | Health check + kill-switch status |
| GET | `/agent-card` | Metadata de l'agent (gouvernance) |

### Exemple de requête

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Je veux obtenir un acte de naissance à Rabat"}'
```

## 📁 Structure du projet

```
egov-maroc-multi-agent/
├── .env.example
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── AGENT_CARD.md
├── RUNBOOK.md
├── src/
│   ├── main.py              # FastAPI + endpoints
│   ├── config.py             # Settings (env vars)
│   ├── graph/
│   │   ├── state.py          # AgentState TypedDict
│   │   ├── supervisor.py     # Supervisor node
│   │   ├── builder.py        # Graph compilation
│   │   └── nodes/
│   │       ├── triage.py     # Classification citoyenne
│   │       ├── document.py   # Actes administratifs
│   │       ├── reclamation.py# Plaintes
│   │       ├── guide.py      # Orientation procédures
│   │       └── monitoring.py # Observabilité
│   ├── models/schemas.py     # Pydantic models
│   ├── middleware/
│   │   ├── correlation.py    # Correlation ID middleware
│   │   └── killswitch.py     # Kill-switch + circuit breaker
│   └── utils/logger.py       # Structured logging
└── tests/
    ├── conftest.py
    ├── test_format.py         # 5 tests format
    ├── test_integration.py    # 5 tests intégration
    ├── test_policy.py         # 5 tests policy
    └── test_bad_input.py      # 5 tests mauvaise entrée
```

## 📜 Licence

MIT — Projet pédagogique ABA Technologie 2026
