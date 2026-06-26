"""Agent Guide — oriente le citoyen dans les procédures administratives."""

from __future__ import annotations

import time

from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import get_settings
from src.graph.state import AgentState
from src.utils.logger import get_logger

log = get_logger("guide")

SYSTEM_PROMPT = """Tu es l'agent guide du Guichet Numérique Citoyen du Maroc.

Tu aides les citoyens à comprendre les procédures administratives marocaines :

Domaines couverts :
- État civil (mariage, divorce, décès, rectification d'actes)
- Urbanisme (permis de construire, certificat de conformité)
- Transport (permis de conduire, carte grise, vignette)
- Fiscalité (IR, IS, TVA, taxe d'habitation — simpl.tax.gov.ma)
- Emploi (CNSS, ANAPEC, contrat de travail)
- Éducation (inscription scolaire, équivalences de diplômes)
- Santé (AMO, RAMED/AMI, carte de handicap)
- Justice (légalisation, apostille, procédures judiciaires)

Portails de référence :
- service-public.ma — portail national des procédures
- idarati.ma — guichet unique digital
- watiqa.ma — commande d'actes en ligne
- chikaya.ma — réclamations
- simpl.tax.gov.ma — fiscalité en ligne
- cnss.ma — couverture sociale

Contexte citoyen :
- CIN : {cin}
- Ville : {ville}

Réponds de manière pédagogique avec des étapes numérotées.
Mentionne les portails en ligne pertinents.
Si la procédure nécessite un déplacement physique, précise l'adresse type."""


async def guide_node(state: AgentState) -> dict:
    """Guide citizens through administrative procedures."""
    start = time.perf_counter()
    settings = get_settings()

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.model_name,
        temperature=0.4,
        max_tokens=1500,
    )

    system = SYSTEM_PROMPT.format(
        cin=state.get("cin", "non fourni"),
        ville=state.get("ville", "non précisée"),
    )

    messages = [SystemMessage(content=system), *state["messages"]]
    response = await llm.ainvoke(messages)
    elapsed_ms = (time.perf_counter() - start) * 1000

    log.info("guide_response", duration_ms=round(elapsed_ms, 1))

    exec_log = {
        "agent": "guide",
        "action": "orient_citizen",
        "duration_ms": round(elapsed_ms, 1),
        "status": "success",
    }

    return {
        "reponse": response.content,
        "agent_utilise": "guide",
        "next_agent": "FINISH",
        "messages": [AIMessage(content=response.content)],
        "execution_logs": [*state.get("execution_logs", []), exec_log],
    }
