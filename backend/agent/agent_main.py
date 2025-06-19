from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from backend.core.config import GEMINI_API_KEY, MODEL_NAME
from backend.tools.feedback_analyzer import analyze_feedback_tool
from backend.tools.prioritizer import prioritize_features_tool, FeatureToPrioritize
from backend.tools.story_writer import write_user_story_tool

# ---------------------------------------------------------------------------
# État de l'agent (persisté par LangGraph entre les tours)
# ---------------------------------------------------------------------------
class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    analysis_result: Optional[Dict[str, Any]]
    prioritization_result: Optional[Dict[str, Any]]
    user_story: Optional[Dict[str, Any]]

# ---------------------------------------------------------------------------
# LLM supervisor configuré avec les trois outils (function‑calling)
# ---------------------------------------------------------------------------
llm_supervisor = (
    ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=GEMINI_API_KEY,
    )
    .bind_tools([
        analyze_feedback_tool,
        prioritize_features_tool,
        write_user_story_tool,
    ])
)

# ---------------------------------------------------------------------------
# Nœud unique : laisse Gemini décider, exécute les tool_calls, met à jour l'état
# ---------------------------------------------------------------------------

def supervisor_step(state: AgentState) -> Dict[str, Any]:
    """Exécute un tour de conversation avec décision et appels d'outils."""

    history: List[BaseMessage] = state.get("messages", [])

    # 1. Premier appel au LLM
    response = llm_supervisor.invoke(history)

    updates: Dict[str, Any] = {}

    # 2. Tant que le LLM renvoie des tool_calls, on les exécute puis on relance le LLM
    loop_guard = 0
    while isinstance(response, AIMessage) and getattr(response, "tool_calls", None):
        loop_guard += 1
        if loop_guard > 20:  # sécurité pour éviter une boucle infinie
            updates["error"] = "Boucle limitée à 20 itérations pour éviter une boucle infinie."
            break

        # a) On ajoute d'abord l'AIMessage (tool_calls) à l'historique
        history.append(response)

        for call in response.tool_calls:
            tool_name: str = call["name"]
            arguments: Dict[str, Any] = call.get("args", {})

            # ------------------------------------------------------------
            # Route vers le bon outil + sérialisation du résultat
            # ------------------------------------------------------------
            serializable_result: Dict[str, Any]
            if tool_name == analyze_feedback_tool.name:
                raw = analyze_feedback_tool.invoke(arguments)
                serializable_result = raw.model_dump()
                updates["analysis_result"] = serializable_result
            elif tool_name == prioritize_features_tool.name:
                features_objs = [FeatureToPrioritize(**f) for f in arguments.get("features", [])]
                raw = prioritize_features_tool.invoke(
                    {
                        "features": features_objs,
                        "framework": arguments.get("framework", "RICE"),
                    }
                )
                serializable_result = raw.model_dump()
                updates["prioritization_result"] = serializable_result
            elif tool_name == write_user_story_tool.name:
                raw = write_user_story_tool.invoke(arguments)
                serializable_result = raw.model_dump()
                updates["user_story"] = serializable_result
            else:
                serializable_result = {"error": f"Outil inconnu : {tool_name}"}

            # Injection du ToolMessage dans l'historique
            tool_call_id = call.get("id", tool_name)
            history.append(
                ToolMessage(
                    content=json.dumps(serializable_result, ensure_ascii=False),
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                )
            )

        # b) Relance du LLM avec l'historique enrichi
        response = llm_supervisor.invoke(history)

    # 3. Ajout de la réponse finale à l'historique
    if isinstance(response, BaseMessage):
        history.append(response)

    # 4. Mise à jour de l'état
    updates["messages"] = history
    return updates

# ---------------------------------------------------------------------------
# Construction du graphe LangGraph (un nœud)
# ---------------------------------------------------------------------------

graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor_step)

graph.set_entry_point("supervisor")

graph.add_edge("supervisor", END)

agent = graph.compile()