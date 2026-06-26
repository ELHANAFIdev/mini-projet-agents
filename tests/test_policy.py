"""Tests POLICY — kill-switch, circuit breaker et limites."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.middleware.killswitch import CircuitBreaker


class TestPolicy:
    """5 tests vérifiant les politiques de sécurité."""

    def test_kill_switch_env_blocks_invoke(self, client):
        """Kill-switch activé par env → 503 sur /invoke."""
        with patch("src.main.is_killed", return_value=True):
            resp = client.post("/invoke", json={"message": "test demande valide"})
            assert resp.status_code == 503
            assert "kill-switch" in resp.json()["detail"].lower()

    def test_kill_switch_file_flag(self):
        """Kill-switch par fichier flag fonctionne."""
        from src.config import Settings
        with tempfile.NamedTemporaryFile(suffix=".flag", delete=False) as f:
            flag_path = f.name
        try:
            s = Settings(kill_switch_file=flag_path, kill_switch_enabled=False, groq_api_key="test")
            assert s.is_killed is True
        finally:
            Path(flag_path).unlink(missing_ok=True)

    def test_circuit_breaker_opens_after_threshold(self, circuit_breaker):
        """Le circuit breaker s'ouvre après N erreurs consécutives."""
        for i in range(3):
            circuit_breaker.record_failure(f"error_{i}")
        assert circuit_breaker.is_open is True

    def test_circuit_breaker_resets_on_success(self, circuit_breaker):
        """Un succès reset le compteur d'erreurs."""
        circuit_breaker.record_failure("err1")
        circuit_breaker.record_failure("err2")
        circuit_breaker.record_success()
        assert circuit_breaker.is_open is False
        # One more error should not open it
        circuit_breaker.record_failure("err3")
        assert circuit_breaker.is_open is False

    def test_circuit_breaker_blocks_invoke(self, client):
        """Circuit breaker ouvert → 503 sur /invoke."""
        with patch("src.main.circuit_breaker") as mock_cb:
            mock_cb.is_open = True
            resp = client.post("/invoke", json={"message": "test circuit breaker"})
            assert resp.status_code == 503
            assert "circuit-breaker" in resp.json()["detail"].lower()
