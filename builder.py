"""Construction et compilation du graphe LangGraph Supervisor."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.graph.nodes.document import document_node
from src.graph.nodes.guide import guide_node
from src.graph.nodes.monitoring import monitoring_node
from src.graph.nodes.reclamation import reclamation_node
from src.graph.nodes.triage import triage_node
from src.graph.state import AgentState
from src.graph.supervisor import supervisor_node
from src.utils.logger import get_logger

log = get_logger("builder")


def _route_supervisor(state: AgentState) -> str:
    """Conditional edge : lit state['next_agent'] et route vers le bon nœud."""
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH":
        return END
    return next_agent


def build_graph() -> StateGraph:
    """Construit et compile le graphe multi-agent Supervisor."""
    graph = StateGraph(AgentState)

    # ── Nœuds ────────────────────────────────────────────────
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("triage", triage_node)
    graph.add_node("document", document_node)
    graph.add_node("reclamation", reclamation_node)
    graph.add_node("guide", guide_node)
    graph.add_node("monitoring", monitoring_node)

    # ── Edges ────────────────────────────────────────────────
    # Point d'entrée → Supervisor
    graph.set_entry_point("supervisor")

    # Supervisor → routing conditionnel
    graph.add_conditional_edges(
        "supervisor",
        _route_supervisor,
        {
            "triage": "triage",
            "document": "document",
            "reclamation": "reclamation",
            "guide": "guide",
            "monitoring": "monitoring",
            END: END,
        },
    )

    # Chaque agent spécialisé retourne au Supervisor
    for agent in ["triage", "document", "reclamation", "guide", "monitoring"]:
        graph.add_edge(agent, "supervisor")

    log.info("graph_built", nodes=6, edges=7)
    return graph.compile()


# Singleton — compilé une seule fois au démarrage
compiled_graph = build_graph()
