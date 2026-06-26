"""Tests MAUVAISE ENTRÉE — requêtes invalides et cas limites."""

from __future__ import annotations

import pytest


class TestBadInput:
    """5 tests vérifiant la gestion des entrées invalides."""

    def test_empty_message_rejected(self, client):
        """Message vide → 422 (validation Pydantic)."""
        resp = client.post("/invoke", json={"message": ""})
        assert resp.status_code == 422

    def test_too_short_message_rejected(self, client):
        """Message trop court (< 3 chars) → 422."""
        resp = client.post("/invoke", json={"message": "ab"})
        assert resp.status_code == 422

    def test_invalid_cin_format_rejected(self, client):
        """CIN invalide (format incorrect) → 422."""
        resp = client.post("/invoke", json={
            "message": "Je veux un acte de naissance",
            "cin": "123INVALID"  # doit être [A-Z]{1,2}\d{5,7}
        })
        assert resp.status_code == 422

    def test_missing_body_rejected(self, client):
        """Requête sans body → 422."""
        resp = client.post("/invoke")
        assert resp.status_code == 422

    def test_valid_cin_accepted(self, client):
        """CIN valide (ex: AB123456) ne déclenche pas de 422."""
        # Note: will fail with 500 because no real API key,
        # but should NOT be 422 (validation passes)
        resp = client.post("/invoke", json={
            "message": "Je veux un casier judiciaire",
            "cin": "AB123456",
            "ville": "Casablanca",
        })
        # Either 200 (if API key works) or 500 (no real key), but NOT 422
        assert resp.status_code != 422
