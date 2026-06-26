"""Agent Monitoring — observabilité, métriques et alertes."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from langchain_core.messages import AIMessage

from src.graph.state import AgentState
from src.utils.logger import get_logger

log = get_logger("monitoring")

# Seuils d'alerte
LATENCY_THRESHOLD_MS = 5000
MAX_ITERATIONS = 8


async def monitoring_node(state: AgentState) -> dict:
    """Analyse les logs d'exécution, détecte les anomalies, produit un rapport."""
    start = time.perf_counter()
    correlation_id = state.get("correlation_id", "unknown")
    exec_logs = state.get("execution_logs", [])

    # ── Analyse des métriques ────────────────────────────────
    total_duration_ms = sum(entry.get("duration_ms", 0) for entry in exec_logs)
    agents_invoked = [entry.get("agent", "?") for entry in exec_logs]
    errors = [entry for entry in exec_logs if entry.get("status") != "success"]

    alerts: list[str] = []

    # Alerte latence
    if total_duration_ms > LATENCY_THRESHOLD_MS:
        alerts.append(f"LATENCE ÉLEVÉE : {total_duration_ms:.0f}ms (seuil : {LATENCY_THRESHOLD_MS}ms)")

    # Alerte boucle
    iteration = state.get("iteration", 0)
    if iteration >= MAX_ITERATIONS:
        alerts.append(f"BOUCLE DÉTECTÉE : {iteration} itérations (max : {MAX_ITERATIONS})")

    # Alerte erreurs
    if errors:
        alerts.append(f"ERREURS : {len(errors)} erreur(s) détectée(s)")

    # ── Rapport ──────────────────────────────────────────────
    rapport_lines = [
        f"══ Rapport Monitoring ══",
        f"Correlation ID : {correlation_id}",
        f"Timestamp      : {datetime.now(timezone.utc).isoformat()}",
        f"Agents appelés : {' → '.join(agents_invoked)}",
        f"Durée totale   : {total_duration_ms:.0f}ms",
        f"Alertes        : {len(alerts)}",
    ]

    if alerts:
        rapport_lines.append("─── Détail alertes ───")
        for alert in alerts:
            rapport_lines.append(f"  ⚠ {alert}")
            log.warning("monitoring_alert", alert=alert, correlation_id=correlation_id)

    rapport = "\n".join(rapport_lines)

    elapsed_ms = (time.perf_counter() - start) * 1000

    log.info(
        "monitoring_complete",
        correlation_id=correlation_id,
        total_duration_ms=round(total_duration_ms, 1),
        alert_count=len(alerts),
        duration_ms=round(elapsed_ms, 1),
    )

    exec_log = {
        "agent": "monitoring",
        "action": "analyze_execution",
        "duration_ms": round(elapsed_ms, 1),
        "alert_count": len(alerts),
        "status": "success",
    }

    return {
        "messages": [AIMessage(content=rapport)],
        "execution_logs": [*exec_logs, exec_log],
    }
