from typing import List

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from backend.agent.agent_main import agent, AgentState

# Charge les variables d’environnement (.env)
load_dotenv()


def run_cli() -> None:
    """Boucle REPL : envoie l’entrée utilisateur à l’agent et affiche sa réponse."""

    print("Product‑Owner Agent CLI – Ctrl‑C pour quitter.\n")

    state: AgentState = {"messages": []}  # mémoire en RAM
    last_len = 0  # pour afficher seulement les nouveaux messages AI

    try:
        while True:
            try:
                user_input = input("\n>> ").strip()
            except EOFError:
                break  # Ctrl‑D

            if not user_input:
                continue  # ignore lignes vides

            # Ajoute le message utilisateur
            state["messages"].append(HumanMessage(content=user_input))

            # Appelle l’agent
            state = agent.invoke(state)

            # Affiche les nouvelles réponses AI
            new_msgs: List[BaseMessage] = state["messages"][last_len:]
            last_len = len(state["messages"])
            for msg in new_msgs:
                if isinstance(msg, AIMessage):
                    print(msg.content)
    except KeyboardInterrupt:
        pass  # Ctrl‑C

    print("\nSession terminée.")


if __name__ == "__main__":
    run_cli()
