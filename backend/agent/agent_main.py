from backend.tools.feedback_analyzer import analyze_feedback
from backend.tools.prioritizer import prioritize_features_RICE
from backend.tools.story_writer import write_user_story
from backend.core.config import GEMINI_API_KEY, MODEL_NAME

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor

# Outils
analyze_feedback_tool = tool(analyze_feedback)
prioritize_features_RICE_tool = tool(prioritize_features_RICE)
write_user_story_tool = tool(write_user_story)

def create_po_agent():
    """
    Crée et configure un agent ReAct LangChain pour assister un Product Owner.
    L'agent sait analyser les feedbacks, prioriser les features et générer des user stories.
    Retourne un AgentExecutor prêt à l'emploi.
    """
    
    # Chargement du prompt ReAct standard depuis le hub LangChain
    prompt = hub.pull("hwchase17/react")

    # Initialisation du LLM Gemini
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2
    )

    # Liste des outils
    tools = [
        analyze_feedback_tool,
        prioritize_features_RICE_tool,
        write_user_story_tool
    ]

    # Création de l'agent ReAct
    agent = create_react_agent(llm, tools, prompt)

    # Création de l'exécuteur d'agent
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    return agent_executor
