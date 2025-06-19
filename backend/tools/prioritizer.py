def prioritize_features_RICE(features: list[dict]) -> list[dict]:
    """
    Outil de priorisation des fonctionnalités selon le framework RICE.
    À utiliser lorsque tu veux classer objectivement des features en fonction de leur impact, portée, confiance et effort estimé.
    Entrée : une liste de dictionnaires représentant des features (avec au moins un champ 'type' et 'summary').
    Retour : la même liste enrichie d'un score RICE et triée par score décroissant.
    """
    feature_items = [f for f in features if f.get("type") == "feature"]

    if not feature_items:
        print("Aucune feature à prioriser dans la liste fournie.")
        return []
    
    for feature in feature_items:
        print(f"\nFeature : {feature.get('summary', feature) }")

        while True:
            try:
                reach = float(input("  -> Notez le Reach (portée) sur 10 : "))
                impact = float(input("  -> Notez l'Impact sur 10 : "))
                confidence = float(input("  -> Notez la Confidence (confiance) sur 10 : "))
                effort = float(input("  -> Notez l'Effort sur 5 (plus c'est bas, mieux c'est) : "))
                
                if effort == 0:
                    print("Erreur : L'effort ne peut pas être 0. Veuillez réessayer.")
                    continue
                break # Sort de la boucle si toutes les saisies sont valides
            except ValueError:
                print("Erreur : Entrée invalide. Veuillez entrer des nombres valides.")

        rice_score = (reach * impact * confidence) / effort
        feature["rice_score"] = rice_score

    # Tri décroissant par score RICE
    features_sorted = sorted(feature_items, key=lambda x: x.get("rice_score", 0), reverse=True)
    return features_sorted 