"""Tests FORMAT — validation de la structure des réponses API."""

from __future__ import annotations

import pytest


class TestFormat:
    """5 tests vérifiant le format des réponses."""

    def test_health_response_structure(self, client):
        """GET /health retourne tous les champs requis."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "kill_switch" in data
        assert "circuit_breaker_open" in data
        assert "version" in data
        assert "environment" in data

    def test_health_status_values(self, client):
        """Le status est 'healthy' ou 'degraded'."""
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] in ("healthy", "degraded")

    def test_agent_card_structure(self, client):
        """GET /agent-card retourne la carte complète."""
        resp = client.get("/agent-card")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Guichet Numérique Citoyen"
        assert data["version"] == "1.0.0"
        assert len(data["agents"]) == 6
        assert len(data["capabilities"]) >= 4

    def test_agent_card_agents_have_name_and_role(self, client):
        """Chaque agent dans la carte a un name et un role."""
        resp = client.get("/agent-card")
        data = resp.json()
        for agent in data["agents"]:
            assert "name" in agent
            assert "role" in agent
            assert len(agent["name"]) > 0
            assert len(agent["role"]) > 0

    def test_correlation_id_header_in_response(self, client):
        """Les réponses contiennent un header X-Correlation-ID."""
        resp = client.get("/health")
        assert "x-correlation-id" in resp.headers
        # Verify UUID format (8-4-4-4-12)
        corr_id = resp.headers["x-correlation-id"]
        parts = corr_id.split("-")
        assert len(parts) == 5
