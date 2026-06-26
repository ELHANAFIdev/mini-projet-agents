"""Tests INTÉGRATION — flux end-to-end avec mock LLM."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.graph.nodes.triage import triage_node
from src.graph.supervisor import _fallback_routing


class TestIntegration:
    """5 tests d'intégration vérifiant les flux agent."""

    def test_fallback_routing_no_category(self, sample_state):
        """Sans catégorie, le fallback route vers triage."""
        sample_state["categorie"] = ""
        result = _fallback_routing(sample_state)
        assert result == "triage"

    def test_fallback_routing_document(self, sample_state):
        """Catégorie 'document' sans réponse → agent document."""
        sample_state["categorie"] = "document"
        sample_state["reponse"] = ""
        result = _fallback_routing(sample_state)
        assert result == "document"

    def test_fallback_routing_reclamation(self, sample_state):
        """Catégorie 'reclamation' sans réponse → agent reclamation."""
        sample_state["categorie"] = "reclamation"
        sample_state["reponse"] = ""
        result = _fallback_routing(sample_state)
        assert result == "reclamation"

    def test_fallback_routing_with_response_no_monitoring(self, sample_state):
        """Avec réponse mais sans monitoring → monitoring."""
        sample_state["categorie"] = "document"
        sample_state["reponse"] = "Voici votre acte..."
        sample_state["execution_logs"] = [{"agent": "document"}]
        result = _fallback_routing(sample_state)
        assert result == "monitoring"

    def test_fallback_routing_with_response_and_monitoring(self, sample_state):
        """Avec réponse et monitoring fait → FINISH."""
        sample_state["categorie"] = "document"
        sample_state["reponse"] = "Voici votre acte..."
        sample_state["execution_logs"] = [
            {"agent": "document"},
            {"agent": "monitoring"},
        ]
        result = _fallback_routing(sample_state)
        assert result == "FINISH"
