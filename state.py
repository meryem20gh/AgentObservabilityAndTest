from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    correlation_id: str
    user_input: str
    answer: str
    source: str
    knowledge_id: str
    is_injection: bool
    logs: List[Dict[str, Any]]
    
    # NOUVELLE CAPACITÉ : Stockage de la classification de l'intention utilisateur
    user_intent: str