import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.tools.prioritizer import prioritize_features_RICE

def run_test():

    donnees_simulees = [
        {
            "type": "feature",
            "summary": "L'utilisateur souhaite exporter les rapports de projet en PDF.",
            "feature_request": "Exporter les rapports de projet au format PDF."
        },
        {
            "type": "bug",
            "summary": "L'utilisateur ne peut pas se connecter avec son compte Google.",
            "feature_request": None
        },
        {
            "type": "feature",
            "summary": "L'utilisateur veut des modèles pour ne pas recréer les mêmes tâches.",
            "feature_request": "Permettre de créer des templates de tâches ou de projets."
        },
        {
            "type": "feature",
            "summary": "L'utilisateur souhaite pouvoir attacher des fichiers aux tâches.",
            "feature_request": "Permettre d'attacher des fichiers directement aux tâches."
        }
    ]

    print("\nDonnées simulées envoyées à prioritize_features_RICE :\n" + json.dumps(donnees_simulees, indent=2, ensure_ascii=False))
    
    # Appel de la fonction à tester de manière interactive
    try:
        print("\nLancement de la priorisation interactive...")
        resultat = prioritize_features_RICE(donnees_simulees)
        print("\nRésultat priorisé :\n" + json.dumps(resultat, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nErreur lors de l'appel à prioritize_features_RICE : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()