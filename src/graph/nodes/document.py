"""Agent Document — traite les demandes d'actes administratifs marocains."""

from __future__ import annotations

import time

from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import get_settings
from src.graph.state import AgentState
from src.utils.logger import get_logger

log = get_logger("document")

SYSTEM_PROMPT = """Tu es l'agent spécialisé dans les documents administratifs du Maroc.

Tu traites les demandes de :
- Acte de naissance → Bureau d'état civil de la commune de naissance
- Casier judiciaire (bulletin n°3) → Tribunal de première instance ou watiqa.ma
- Attestation de résidence → Moqaddem du quartier puis Caïd/Pachalik
- Certificat de vie → Commune de résidence

Pour chaque demande, fournis :
1. Les documents nécessaires (CIN, photos, timbres fiscaux…)
2. L'administration compétente et son adresse type
3. Le délai estimé de traitement
4. Les frais (timbres, droits…)
5. Possibilité de demande en ligne (portails : watiqa.ma, chikaya.ma, etc.)

Contexte citoyen :
- CIN : {cin}
- Ville : {ville}
- Sous-type demandé : {sous_type}

Réponds de manière claire, structurée et en darija/français accessible.
Termine par un résumé des étapes à suivre."""


async def document_node(state: AgentState) -> dict:
    """Process administrative document requests."""
    start = time.perf_counter()
    settings = get_settings()

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.model_name,
        temperature=0.3,
        max_tokens=1500,
    )

    system = SYSTEM_PROMPT.format(
        cin=state.get("cin", "non fourni"),
        ville=state.get("ville", "non précisée"),
        sous_type=state.get("sous_type", "non précisé"),
    )

    messages = [SystemMessage(content=system), *state["messages"]]
    response = await llm.ainvoke(messages)
    elapsed_ms = (time.perf_counter() - start) * 1000

    log.info(
        "document_response",
        sous_type=state.get("sous_type"),
        duration_ms=round(elapsed_ms, 1),
    )

    exec_log = {
        "agent": "document",
        "action": "process_document_request",
        "sous_type": state.get("sous_type", ""),
        "duration_ms": round(elapsed_ms, 1),
        "status": "success",
    }

    return {
        "reponse": response.content,
        "agent_utilise": "document",
        "next_agent": "FINISH",
        "messages": [AIMessage(content=response.content)],
        "execution_logs": [*state.get("execution_logs", []), exec_log],
    }
