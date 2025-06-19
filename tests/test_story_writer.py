import sys
import os

# Ajout du répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.tools.story_writer import write_user_story

def run_test():
    # Définir une description de fonctionnalité simulée
    feature_description = "Permettre aux utilisateurs d'exporter les rapports de projet au format PDF pour les partager facilement."

    print("\nDescription envoyée à write_user_story :\n" + feature_description + "\n")

    try:
        print("Lancement de la génération de la User Story...")
        result = write_user_story(feature_description)
        print("\nUser Story générée :\n" + (result if result else "Aucune User Story n'a été retournée."))
    except Exception as e:
        print(f"\nErreur lors de l'appel à write_user_story : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
