from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.core.config import GEMINI_API_KEY, MODEL_NAME

def write_user_story(feature_description: str) -> str:
    """
    Outil de génération de User Story au format Product Owner.
    À utiliser lorsque tu veux transformer une description de fonctionnalité en une User Story complète avec critères d'acceptation.
    Entrée : une chaîne de caractères décrivant la fonctionnalité à formaliser.
    Retour : une User Story rédigée en Markdown, prête à être intégrée dans un backlog.
    """
    prompt = PromptTemplate(
        template=(
            "Tu es un Product Owner expert en rédaction de User Stories. "
            "À partir de la description suivante, rédige une User Story complète au format Markdown, selon ce modèle :\n\n"
            "### User Story\n"
            "**En tant que** [type d'utilisateur], **je veux** [action] **afin de** [bénéfice].\n\n"
            "### Critères d'Acceptation\n"
            "* **Scénario 1:** ...\n"
            "    * **Étant donné** ...\n"
            "    * **Lorsque** ...\n"
            "    * **Alors** ...\n"
            "* **Scénario 2:** ...\n\n"
            "Description de la fonctionnalité : {feature_description}"
        ),
        input_variables=["feature_description"]
    )
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.3
    )
    chain = prompt | llm
    print("Génération de la User Story en cours...")
    result = chain.invoke({"feature_description": feature_description})
    return result.content 