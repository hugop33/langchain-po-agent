from typing import List
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from backend.core.config import GEMINI_API_KEY, MODEL_NAME


# --- Schéma de données ---
class UserStory(BaseModel):
    """
    Représente une User Story complète générée pour une fonctionnalité.
    """
    title: str = Field(description="Titre concis de la User Story.")
    story: str = Field(description="Description narrative de la User Story.")
    acceptance_criteria: List[str] = Field(description="Liste des critères d'acceptation.")
    estimated_complexity: str = Field(description="Estimation de la complexité (faible, moyen, élevé).")


# --- Outil de génération de User Story ---
@tool
def write_user_story_tool(feature_description: str) -> UserStory:
    """
    Génère une User Story structurée, incluant les critères d'acceptation et l'estimation de complexité, à partir d'une description de fonctionnalité.
    """
    # 1. Initialisation du parser de sortie
    output_parser = PydanticOutputParser(pydantic_object=UserStory)

    # 2. Initialisation du modèle LLM Gemini
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.7,  # Température modérée pour la créativité
        api_key=GEMINI_API_KEY
    )

    # 3. Création du prompt template
    prompt = PromptTemplate(
        template="""
        Vous êtes un expert en gestion de produit et en rédaction agile. À partir de la description de la fonctionnalité suivante :
        ---
        {feature_description}
        ---
        Générez une User Story complète au format JSON avec ces champs :
        - title : un titre concis sous forme 'En tant que..., je veux..., afin de...'.
        - story : une description narrative plus détaillée.
        - acceptance_criteria : une liste de critères d'acceptation clairs et testables.
        - estimated_complexity : estimation de la complexité (faible, moyen ou élevé).

        Retournez la sortie strictement au format JSON conforme à ces instructions :
        {format_instructions}
        """,
        input_variables=["feature_description"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    # 4. Création de la chaîne d'analyse
    chain = prompt | llm | output_parser

    # 5. Lancement de la génération
    print("--- Génération de la User Story ---")
    result = chain.invoke({"feature_description": feature_description})
    print("--- User Story générée ---")
    return result
