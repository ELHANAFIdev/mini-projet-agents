import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.middleware.killswitch import CircuitBreaker

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def circuit_breaker():
    return CircuitBreaker()

@pytest.fixture
def sample_state():
    return {
        "messages": [],
        "demande": "",
        "cin": "",
        "ville": "",
        "categorie": "",
        "sous_type": "",
        "reponse": "",
        "agent_utilise": "",
        "next_agent": "",
        "correlation_id": "test-id",
        "execution_logs": [],
        "iteration": 0,
    }
