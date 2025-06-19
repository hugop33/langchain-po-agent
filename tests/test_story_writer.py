def test_story_writer():
    from backend.tools.story_writer import write_user_story_tool, GEMINI_API_KEY
    from dotenv import load_dotenv
    load_dotenv()

    if not GEMINI_API_KEY:
        print("Erreur: La variable d'environnement GEMINI_API_KEY n'est pas définie.")
    else:
        feature_description = (
            "Permettre aux utilisateurs de s'inscrire via OAuth et gérer les sessions de façon sécurisée."
        )
        user_story = write_user_story_tool.invoke({"feature_description": feature_description})
        print("--- Résultat de la Génération de la User Story ---")
        print(f"Title: {user_story.title}")
        print(f"Story: {user_story.story}")
        print("Acceptance Criteria:")
        for idx, crit in enumerate(user_story.acceptance_criteria, start=1):
            print(f"  {idx}. {crit}")
        print(f"Estimated Complexity: {user_story.estimated_complexity}")

if __name__ == '__main__':
    test_story_writer()
