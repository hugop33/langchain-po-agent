def test_feedback_analyzer():
    from backend.tools.feedback_analyzer import analyze_feedback_tool, GEMINI_API_KEY
    from dotenv import load_dotenv
    load_dotenv()

    if not GEMINI_API_KEY:
        print("Erreur: La variable d'environnement GEMINI_API_KEY n'est pas définie.")
    else:
        sample_feedback = (
            """
            Analyse ces feedback : \"J'aimerais vraiment pouvoir exporter mes rapports de projet au format PDF.\", \"Impossible de me connecter via mon compte Google. La page se recharge sans rien faire.\", \"Je perds un temps fou à devoir recréer les mêmes types de tâches pour chaque nouveau projet.\", \"Le défilement dans la vue Kanban est très saccadé sur Firefox. Au fait, ce serait génial si on pouvait attacher des fichiers directement aux tâches.\", \"La dernière mise à jour de l'interface est magnifique ! Bravo à l'équipe.\"
            """
        )
        analysis_result = analyze_feedback_tool.invoke(sample_feedback)
        print("\n--- Résultat de l'Analyse ---")
        if analysis_result and analysis_result.features:
            for feature in analysis_result.features:
                print(f"\n+ Feature Name: {feature.name}")
                print(f"   Description: {feature.description}")
                print(f"   Source Feedbacks:")
                for source in feature.source_feedbacks:
                    print(f"     - \"{source}\"")
        else:
            print("Aucune fonctionnalité exploitable n'a été extraite.")

if __name__ == '__main__':
    test_feedback_analyzer()
