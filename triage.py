"""Agent Triage — classifie la demande citoyenne."""

from __future__ import annotations

import json
import time

from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import get_settings
from src.graph.state import AgentState
from src.utils.logger import get_logger

log = get_logger("triage")

SYSTEM_PROMPT = """Tu es l'agent de triage du Guichet Numérique Citoyen du Maroc.

Ton rôle : classifier la demande du citoyen dans UNE des catégories suivantes.

Catégories :
- "document"     → demande d'acte administratif (naissance, résidence, casier judiciaire, certificat de vie)
- "reclamation"  → plainte contre une administration publique marocaine
- "guide"        → question sur une procédure administrative ou orientation
- "suivi"        → suivi d'un dossier existant (numéro de dossier mentionné)
- "inconnu"      → demande hors périmètre ou incompréhensible

Réponds UNIQUEMENT en JSON strict :
{"categorie": "<valeur>", "sous_type": "<précision ou vide>", "confiance": <0.0-1.0>}

Exemples de sous_type pour "document" :
- acte_naissance, casier_judiciaire, attestation_residence, certificat_vie

Ne fournis aucun texte en dehors du JSON."""


async def triage_node(state: AgentState) -> dict:
    """Classify citizen request into a category."""
    start = time.perf_counter()
    settings = get_settings()

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.model_name,
        temperature=0,
        max_tokens=200,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = await llm.ainvoke(messages)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Parse JSON response
    try:
        raw = response.content.strip()
        # Handle markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        parsed = json.loads(raw)
        categorie = parsed.get("categorie", "inconnu")
        sous_type = parsed.get("sous_type", "")
    except (json.JSONDecodeError, IndexError):
        log.warning("triage_parse_error", raw=response.content[:200])
        categorie = "inconnu"
        sous_type = ""

    log.info(
        "triage_complete",
        categorie=categorie,
        sous_type=sous_type,
        duration_ms=round(elapsed_ms, 1),
    )

    exec_log = {
        "agent": "triage",
        "action": "classify",
        "categorie": categorie,
        "sous_type": sous_type,
        "duration_ms": round(elapsed_ms, 1),
        "status": "success",
    }

    return {
        "categorie": categorie,
        "sous_type": sous_type,
        "agent_utilise": "triage",
        "messages": [AIMessage(content=f"[Triage] Catégorie détectée : {categorie} / {sous_type}")],
        "execution_logs": [*state.get("execution_logs", []), exec_log],
    }
