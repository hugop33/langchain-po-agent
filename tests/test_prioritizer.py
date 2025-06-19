def test_prioritizer():
    from backend.tools.prioritizer import prioritize_features_tool, FeatureToPrioritize, GEMINI_API_KEY
    from dotenv import load_dotenv
    load_dotenv()

    if not GEMINI_API_KEY:
        print("Erreur: La variable d'environnement GEMINI_API_KEY n'est pas définie.")
    else:
        sample_features = [
            FeatureToPrioritize(
                name="Export PDF",
                description="Permettre l'export des rapports de projet au format PDF."
            ),
            FeatureToPrioritize(
                name="Drag & Drop Fichiers",
                description="Support du glisser-déposer de plusieurs fichiers dans l'interface."
            ),
            FeatureToPrioritize(
                name="Intégration Google Auth",
                description="Permettre la connexion via un compte Google de manière fluide."
            ),
        ]
        prioritization_result = prioritize_features_tool.invoke({
            "features": sample_features,
            "framework": "RICE"
        })
        print("\n--- Résultat de la Priorisation ---")
        for pf in prioritization_result.features:
            print(f"\n* {pf.feature_name} -> Score final: {pf.final_score}")
            print(f"  Détails des scores: {pf.score}")
            print(f"  Justification: {pf.justification}")

if __name__ == '__main__':
    test_prioritizer()
