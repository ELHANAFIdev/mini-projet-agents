from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class InvokeRequest(BaseModel):
    message: str = Field(..., min_length=3)
    cin: Optional[str] = Field(default=None, pattern=r"^[A-Z]{1,2}\d{5,7}$")
    ville: Optional[str] = None

class InvokeResponse(BaseModel):
    correlation_id: str
    categorie: str
    reponse: str
    agent_utilise: str
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    kill_switch: bool
    circuit_breaker_open: bool
    environment: str
    version: str = "1.0.0"

class AgentCardResponse(BaseModel):
    name: str
    version: str
    description: str
    authors: List[str]
    capabilities: List[str]
    agents: List[Dict[str, Any]]
    deployment: Dict[str, Any]
