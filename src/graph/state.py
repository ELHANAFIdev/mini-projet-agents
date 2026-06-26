from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    demande: str
    cin: str
    ville: str
    categorie: str
    sous_type: str
    reponse: str
    agent_utilise: str
    next_agent: str
    correlation_id: str
    execution_logs: List[Dict[str, Any]]
    iteration: int
