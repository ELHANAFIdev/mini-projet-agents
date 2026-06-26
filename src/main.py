"""Guichet Numérique Citoyen — FastAPI server wrapping LangGraph multi-agent."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from src.config import get_settings
from src.graph.builder import compiled_graph
from src.middleware.correlation import CorrelationIdMiddleware
from src.middleware.killswitch import circuit_breaker, is_killed
from src.models.schemas import (
    AgentCardResponse,
    HealthResponse,
    InvokeRequest,
    InvokeResponse,
)
from src.utils.logger import get_logger, setup_logging


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    setup_logging()
    log = get_logger("main")
    log.info("startup", version="1.0.0", env=get_settings().app_env)
    yield
    log.info("shutdown")


app = FastAPI(
    title="Guichet Numérique Citoyen — e-Gov Maroc",
    description="Architecture multi-agent LangGraph (Supervisor) pour les services publics marocains",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

log = get_logger("main")


# ── Endpoints ────────────────────────────────────────────────
@app.post("/invoke", response_model=InvokeResponse)
async def invoke(request: Request, body: InvokeRequest):
    """Soumettre une demande citoyenne au graphe multi-agent."""

    # Kill-switch check
    if is_killed():
        raise HTTPException(status_code=503, detail="Service désactivé (kill-switch actif)")

    # Circuit-breaker check
    if circuit_breaker.is_open:
        raise HTTPException(status_code=503, detail="Service temporairement indisponible (circuit-breaker ouvert)")

    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    # Préparer l'état initial
    initial_state = {
        "messages": [HumanMessage(content=body.message)],
        "demande": body.message,
        "cin": body.cin or "",
        "ville": body.ville or "",
        "categorie": "",
        "sous_type": "",
        "reponse": "",
        "agent_utilise": "",
        "next_agent": "",
        "correlation_id": correlation_id,
        "execution_logs": [],
        "iteration": 0,
    }

    try:
        result = await compiled_graph.ainvoke(initial_state)
        circuit_breaker.record_success()

        log.info(
            "invoke_complete",
            categorie=result.get("categorie"),
            agent=result.get("agent_utilise"),
            iterations=result.get("iteration"),
        )

        return InvokeResponse(
            correlation_id=correlation_id,
            categorie=result.get("categorie", "inconnu"),
            reponse=result.get("reponse", "Aucune réponse générée."),
            agent_utilise=result.get("agent_utilise", "unknown"),
            metadata={
                "iterations": result.get("iteration", 0),
                "sous_type": result.get("sous_type", ""),
                "execution_logs": result.get("execution_logs", []),
            },
        )

    except Exception as exc:
        circuit_breaker.record_failure(str(exc))
        log.error("invoke_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Erreur de traitement : {exc}") from exc


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check avec statut kill-switch et circuit-breaker."""
    settings = get_settings()
    return HealthResponse(
        status="degraded" if is_killed() or circuit_breaker.is_open else "healthy",
        kill_switch=is_killed(),
        circuit_breaker_open=circuit_breaker.is_open,
        environment=settings.app_env,
    )


@app.get("/agent-card", response_model=AgentCardResponse)
async def agent_card():
    """Retourne la carte d'identité de l'agent (gouvernance)."""
    return AgentCardResponse(
        name="Guichet Numérique Citoyen",
        version="1.0.0",
        description="Architecture multi-agent Supervisor LangGraph pour la digitalisation des services publics marocains.",
        authors=["ABA Technologie"],
        capabilities=[
            "Classification de demandes citoyennes (triage)",
            "Traitement des demandes d'actes administratifs",
            "Gestion des réclamations (chikaya.ma)",
            "Orientation procédures administratives",
            "Observabilité et monitoring avec Correlation ID",
        ],
        agents=[
            {"name": "supervisor", "role": "Orchestration et routing"},
            {"name": "triage", "role": "Classification des demandes"},
            {"name": "document", "role": "Actes administratifs"},
            {"name": "reclamation", "role": "Plaintes citoyennes"},
            {"name": "guide", "role": "Orientation procédures"},
            {"name": "monitoring", "role": "Observabilité et alertes"},
        ],
        deployment={
            "runtime": "Python 3.11+ / FastAPI / Uvicorn",
            "container": "Docker",
            "ci_cd": "GitHub Actions",
            "cloud": "Render / Railway",
        },
    )
