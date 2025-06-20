from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage

from backend.core.config import GEMINI_API_KEY, MODEL_NAME
from backend.tools.feedback_analyzer import analyze_feedback_tool, identify_recurrent_patterns_tool
from backend.tools.prioritizer import prioritize_features_tool, FeatureToPrioritize
from backend.tools.story_writer import write_user_story_tool

# --- Schéma d'état de l'agent (persisté par LangGraph entre les tours) ---
class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    analysis_result: Optional[Dict[str, Any]]
    prioritization_result: Optional[Dict[str, Any]]
    user_story: Optional[Dict[str, Any]]

# --- LLM supervisor configuré avec les outils (function-calling) ---
llm_supervisor = (
    ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=GEMINI_API_KEY,
    )
    .bind_tools([
        analyze_feedback_tool,
        identify_recurrent_patterns_tool,
        prioritize_features_tool,
        write_user_story_tool,
    ])
)

# --- Nœud principal : décision, exécution des outils, mise à jour de l'état ---
def supervisor_step(state: AgentState) -> Dict[str, Any]:
    """
    Exécute un tour de conversation avec décision et appels d'outils.
    """
    # 1. Création du message système
    system_msg = SystemMessage(
        content=(
            "You are a Product‑Owner assistant. "
            "You have four tools:\n"
            "  - analyze_feedback   – analyse and extract structured feature requests from raw feedbacks.\n"
            "  - identify_recurrent_patterns – detect recurring patterns ONLY if the user explicitly asks (keywords: 'pattern', 'thème récurrent', 'tendance', 'recurrence').\n"
            "  - prioritize_features – score or rank features when the user requests prioritisation.\n"
            "  - write_user_story    – create a user story when the user asks for it.\n"
            "If the user provides several feedbacks at once, always send the full list together to the analyze_feedback tool for a global analysis.\n"
            "For each user request, determine which steps are relevant (analysis, prioritisation, user‑story writing) and call the tools in a logical order. "
            "Output :"
            "For feature prioritization, for each feature, always display the 'score' field exactly as returned by the tool (with all sub-scores and justifications), the final_score, and the justification." 
            "Present the results and resume the steps taken in a clear and concise manner. "
            "Avoid HTML/Markdown formatting because the output will be used in a CLI application, use plain text instead."
        )
    )

    history: List[BaseMessage] = state.get("messages", [])

    # 2. Insère un message système une seule fois, en tête de l'historique
    if not history or not isinstance(history[0], SystemMessage):
        history = [system_msg] + history

    # 3. Premier appel au LLM
    response = llm_supervisor.invoke(history)

    updates: Dict[str, Any] = {}

    # 4. Boucle d'exécution des tool_calls
    loop_guard = 0
    while isinstance(response, AIMessage) and getattr(response, "tool_calls", None):
        loop_guard += 1
        
        if loop_guard > 20:
            updates["error"] = "Boucle limitée à 20 itérations pour éviter une boucle infinie."
            break

        # Ajoute le message AI contenant les tool_calls dans l'historique
        history.append(response)

        for call in response.tool_calls:
            tool_name: str = call["name"]
            arguments: Dict[str, Any] = call.get("args", {})

            # --- Routage vers le bon outil et sérialisation du résultat ---
            if tool_name == analyze_feedback_tool.name:
                result = analyze_feedback_tool.invoke(arguments)
                serializable = result.model_dump()
                updates["analysis_result"] = serializable

            elif tool_name == prioritize_features_tool.name: # Prioritization tool
                features_objs = [FeatureToPrioritize(**f) for f in arguments.get("features", [])]
                result = prioritize_features_tool.invoke({
                    "features": features_objs,
                    "framework": arguments.get("framework", "RICE"),
                    }
                )
                serializable = result.model_dump()
                updates["prioritization_result"] = serializable

            elif tool_name == write_user_story_tool.name: # Story writing tool
                result = write_user_story_tool.invoke(arguments)
                serializable = result.model_dump()
                updates["user_story"] = serializable

            elif tool_name == identify_recurrent_patterns_tool.name: # Pattern analysis tool
                result = identify_recurrent_patterns_tool.invoke(arguments)
                serializable = result.model_dump()

            else: # Outil inconnu
                serializable = {"error": f"Outil inconnu : {tool_name}"}

            # Injection d'un ToolMessage avec un id correct
            tool_call_id = call.get("id", tool_name)
            history.append(
                ToolMessage(
                    content=json.dumps(serializable, ensure_ascii=False),
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                )
            )

        # Relance du LLM avec l'historique enrichi
        response = llm_supervisor.invoke(history)

    # 5. Ajout de la réponse finale à l'historique
    if isinstance(response, BaseMessage):
        history.append(response)

    # 6. Mise à jour de l'état
    updates["messages"] = history

    # On conserve les anciens résultats s'ils existent déjà dans le state
    # for key in ["analysis_result", "prioritization_result", "user_story"]:
    #     if key not in updates and key in state:
    #         updates[key] = state[key]

    return updates

# --- Construction du graphe LangGraph (un nœud) ---
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor_step)

graph.set_entry_point("supervisor")

graph.add_edge("supervisor", END)

agent = graph.compile()