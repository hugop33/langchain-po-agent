from typing import List

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from backend.agent.agent_main import agent, AgentState

# --- Chargement des variables d'environnement (.env) ---
load_dotenv()

# --- Boucle REPL principale pour l'agent Product Owner ---
def run_cli() -> None:
    """
    Boucle REPL : envoie l'entrée utilisateur à l'agent et affiche sa réponse.
    """
    print("Product‑Owner Agent CLI – Ctrl‑C pour quitter.\n")

    state: AgentState = {"messages": []}  # mémoire en RAM
    last_len = 0  # pour afficher seulement les nouveaux messages AI

    try:
        while True:
            user_input = input("\n>> ").strip()
            
            if not user_input:
                continue  # ignore les lignes vides

            # 1. Ajoute le message utilisateur
            state["messages"].append(HumanMessage(content=user_input))

            # 2. Appelle l'agent
            state = agent.invoke(state)

            # 3. Affiche les nouvelles réponses AI
            new_msgs: List[BaseMessage] = state["messages"][last_len:]
            last_len = len(state["messages"])

            for msg in new_msgs:
                if isinstance(msg, AIMessage):
                    print(msg.content)

    except KeyboardInterrupt:
        pass  # Ctrl‑C pour quitter

    print("\nSession terminée.")


if __name__ == "__main__":
    run_cli()
