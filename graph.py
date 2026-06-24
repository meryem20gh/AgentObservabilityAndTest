from typing import Literal
from langgraph.graph import StateGraph, END

# Verify paths match your package workspace setup
from state import AgentState
from agents import (
    guardrail_agent,
    intent_classification_agent,  # <-- Importé depuis agents.py
    knowledge_agent,
    fallback_agent
)

# Router after Guardrail check
def guardrail_router(state) -> Literal["intent_classification_agent", "__end__"]:
    if state.get("is_injection", False):
        return "__end__"  # Skip execution entirely if malicious
    return "intent_classification_agent"  # Oriente vers la classification si SAFE

# Router after Knowledge evaluation
def knowledge_router(state) -> Literal["fallback_agent", "__end__"]:
    if state["answer"] == "":
        return "fallback_agent"
    return "__end__"

graph = StateGraph(AgentState)

# ==========================
# NODES
# ==========================
graph.add_node("guardrail_agent", guardrail_agent)
graph.add_node("intent_classification_agent", intent_classification_agent)  # <-- Ajout du nœud
graph.add_node("knowledge_agent", knowledge_agent)
graph.add_node("fallback_agent", fallback_agent)

# ==========================
# ENTRY POINT
# ==========================
graph.set_entry_point("guardrail_agent") # Entry point is now Security Guardrail

# ==========================
# ROUTING
# ==========================
graph.add_conditional_edges(
    "guardrail_agent",
    guardrail_router,
    {
        "intent_classification_agent": "intent_classification_agent",
        "__end__": END
    }
)

# Arête directe : Une fois l'intention classifiée, on passe automatiquement à la recherche
graph.add_edge("intent_classification_agent", "knowledge_agent")

graph.add_conditional_edges(
    "knowledge_agent",
    knowledge_router,
    {
        "fallback_agent": "fallback_agent",
        "__end__": END
    }
)

graph.add_edge("fallback_agent", END)

# ==========================
# COMPILE
# ==========================
app = graph.compile()