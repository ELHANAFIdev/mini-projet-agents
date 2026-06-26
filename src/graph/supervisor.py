"""Supervisor — orchestre les agents spécialisés via routing LLM."""

from __future__ import annotations

import json
import time

from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import get_settings
from src.graph.state import AgentState
from src.utils.logger import get_logger

log = get_logger("supervisor")

AGENTS = ["triage", "document", "reclamation", "guide", "monitoring"]
MAX_ITERATIONS = 8

SYSTEM_PROMPT = """Tu es le Supervisor du Guichet Numérique Citoyen du Maroc.

Tu orchestre les agents spécialisés suivants :
- "triage"       → classifie la demande du citoyen
- "document"     → traite les demandes d'actes administratifs
- "reclamation"  → gère les plaintes citoyennes
- "guide"        → oriente sur les procédures administratives
- "monitoring"   → produit un rapport d'observabilité
- "FINISH"       → la demande est traitée, terminer

Logique de routing :
1. Si aucune catégorie n'est encore définie → "triage"
2. Si catégorie = "document" et pas encore de réponse → "document"
3. Si catégorie = "reclamation" et pas encore de réponse → "reclamation"
4. Si catégorie = "guide" ou "suivi" et pas encore de réponse → "guide"
5. Si une réponse existe → "monitoring" puis "FINISH"
6. Si catégorie = "inconnu" → "guide" (fallback)

Réponds UNIQUEMENT en JSON strict :
{"next": "<nom_agent>", "reason": "<justification courte>"}"""


async def supervisor_node(state: AgentState) -> dict:
    """Decide which agent to invoke next."""
    start = time.perf_counter()
    settings = get_settings()
    iteration = state.get("iteration", 0)

    # Guard anti-boucle infinie
    if iteration >= MAX_ITERATIONS:
        log.error("supervisor_max_iterations", iteration=iteration)
        return {
            "next_agent": "FINISH",
            "iteration": iteration + 1,
        }

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.model_name,
        temperature=0,
        max_tokens=150,
    )

    # Construire le contexte pour le supervisor
    context_parts = [
        f"Catégorie actuelle : {state.get('categorie', 'non définie')}",
        f"Sous-type : {state.get('sous_type', 'non défini')}",
        f"Réponse existante : {'oui' if state.get('reponse') else 'non'}",
        f"Itération : {iteration}",
        f"Agents déjà appelés : {[e.get('agent') for e in state.get('execution_logs', [])]}",
    ]
    context = "\n".join(context_parts)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
        AIMessage(content=f"[Contexte Supervisor]\n{context}"),
    ]

    response = await llm.ainvoke(messages)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Parse routing decision
    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        parsed = json.loads(raw)
        next_agent = parsed.get("next", "FINISH")
        reason = parsed.get("reason", "")
    except (json.JSONDecodeError, IndexError):
        log.warning("supervisor_parse_error", raw=response.content[:200])
        # Fallback heuristic
        next_agent = _fallback_routing(state)
        reason = "fallback heuristic"

    # Validate agent name
    if next_agent not in [*AGENTS, "FINISH"]:
        log.warning("supervisor_invalid_agent", agent=next_agent)
        next_agent = _fallback_routing(state)
        reason = "invalid agent name fallback"

    log.info(
        "supervisor_decision",
        next_agent=next_agent,
        reason=reason,
        iteration=iteration,
        duration_ms=round(elapsed_ms, 1),
    )

    return {
        "next_agent": next_agent,
        "iteration": iteration + 1,
    }


def _fallback_routing(state: AgentState) -> str:
    """Routing heuristique sans LLM en cas d'erreur de parsing."""
    categorie = state.get("categorie", "")
    reponse = state.get("reponse", "")

    if not categorie:
        return "triage"
    if reponse:
        # Si monitoring déjà fait, finish
        agents_done = [e.get("agent") for e in state.get("execution_logs", [])]
        return "FINISH" if "monitoring" in agents_done else "monitoring"
    return {
        "document": "document",
        "reclamation": "reclamation",
        "guide": "guide",
        "suivi": "guide",
    }.get(categorie, "guide")
