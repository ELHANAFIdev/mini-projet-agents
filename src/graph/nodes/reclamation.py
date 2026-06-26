"""Agent Réclamation — gère les plaintes citoyennes contre l'administration."""

from __future__ import annotations

import time

from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import get_settings
from src.graph.state import AgentState
from src.utils.logger import get_logger

log = get_logger("reclamation")

SYSTEM_PROMPT = """Tu es l'agent spécialisé dans les réclamations citoyennes au Maroc.

Portail officiel : chikaya.ma (plateforme nationale de gestion des réclamations).

Ton rôle :
1. Identifier l'administration visée par la plainte
2. Qualifier le type de réclamation (retard, abus, corruption, service défaillant…)
3. Guider le citoyen pour déposer une réclamation sur chikaya.ma
4. Informer sur les délais légaux de réponse (loi 14-55 : 60 jours)
5. Proposer des recours alternatifs si nécessaire :
   - Médiateur du Royaume (Institution Wali Al Madalim)
   - CNDP pour les données personnelles
   - Tribunal administratif pour les litiges

Contexte citoyen :
- CIN : {cin}
- Ville : {ville}

Réponds de manière empathique et structurée.
Donne les étapes concrètes pour le dépôt de la réclamation."""


async def reclamation_node(state: AgentState) -> dict:
    """Process citizen complaints against public administrations."""
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
    )

    messages = [SystemMessage(content=system), *state["messages"]]
    response = await llm.ainvoke(messages)
    elapsed_ms = (time.perf_counter() - start) * 1000

    log.info("reclamation_response", duration_ms=round(elapsed_ms, 1))

    exec_log = {
        "agent": "reclamation",
        "action": "process_complaint",
        "duration_ms": round(elapsed_ms, 1),
        "status": "success",
    }

    return {
        "reponse": response.content,
        "agent_utilise": "reclamation",
        "next_agent": "FINISH",
        "messages": [AIMessage(content=response.content)],
        "execution_logs": [*state.get("execution_logs", []), exec_log],
    }
