from backend.core import config  # Charge les variables d'environnement dès le début
from backend.agent.agent_main import create_po_agent


def main():
    agent = create_po_agent()

    print("\nAssistant Product Owner prêt. Posez votre question.\n")

    while True:
        try:
            user_input = input('> ')
            if not user_input.strip():
                continue

            # On suppose que l'agent attend un dictionnaire avec la clé 'input'
            result = agent.invoke({"input": user_input})

            # Selon la config, la réponse peut être dans 'output' ou directement dans le résultat
            
            if isinstance(result, dict) and "output" in result:
                print(result["output"])

            else:
                print(result)

        except (KeyboardInterrupt, EOFError):
            print("\nAu revoir !")
            break
        except Exception as e:
            print(f"[Erreur] {e}")


if __name__ == "__main__":
    main()
