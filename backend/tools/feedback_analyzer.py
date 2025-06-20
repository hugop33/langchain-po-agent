from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from backend.core.config import GEMINI_API_KEY, MODEL_NAME


# --- Schémas de données ---
class Feature(BaseModel):
    """
    Représente une seule demande de fonctionnalité extraite d'un feedback.
    """
    name: str = Field(description="Un titre court et descriptif pour la fonctionnalité demandée.")
    description: str = Field(description="Une description détaillée de ce que la fonctionnalité devrait faire, basée sur le feedback.")
    source_feedbacks: List[str] = Field(description="Une liste des phrases exactes du feedback qui justifient cette demande de fonctionnalité.")
    category: str = Field(description='Catégorie du feedback : "bug", "feature" ou "comment".')


class AnalysisResult(BaseModel):
    """
    Résultat complet de l'analyse, contenant une liste de toutes les fonctionnalités extraites.
    """
    features: List[Feature] = Field(description="Liste des fonctionnalités extraites du texte de feedback.", default_factory=list)


class PatternAnalysisResult(BaseModel):
    """
    Résultat de l'analyse des patterns récurrents dans les feedbacks.
    """
    patterns: List[str] = Field(description="Liste des patterns ou thèmes récurrents identifiés dans les feedbacks.")


# --- Outils d'analyse de feedback ---
@tool
def analyze_feedback_tool(feedback_text: str) -> AnalysisResult:
    """
    Analyse un texte de feedback utilisateur (email, commentaire, etc.) pour identifier les thèmes récurrents
    et extraire des demandes de fonctionnalités structurées.
    """
    # 1. Initialisation du parser de sortie
    output_parser = PydanticOutputParser(pydantic_object=AnalysisResult)

    # 2. Initialisation du modèle LLM Gemini
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )

    # 3. Création du prompt template
    prompt = PromptTemplate(
        template="""
        Vous êtes un assistant expert pour un Product Owner. Votre rôle est d'analyser le feedback des utilisateurs
        et d'en extraire des demandes de fonctionnalités claires et exploitables.

        Analysez le feedback suivant :
        ---
        {feedback}
        ---

        Identifiez chaque demande de fonctionnalité distincte. Pour chaque demande, fournissez un nom, une description,
        la catégorie ("bug", "feature" ou "comment"), et les extraits exacts du feedback qui la concernent. Ne regroupez que les feedbacks qui parlent
        EXACTEMENT de la même fonctionnalité. Si aucune fonctionnalité n'est mentionnée, retournez une liste vide.

        Retournez la sortie strictement au format JSON conforme à ces instructions :
        {format_instructions}
        """,
        input_variables=["feedback"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    # 4. Création de la chaîne d'analyse
    chain = prompt | llm | output_parser

    # 5. Lancement de l'analyse
    print("--- Lancement de l'analyse des feedbacks ---")
    result = chain.invoke({"feedback": feedback_text})
    print("--- Analyse terminée ---")
    return result


# --- Outils d'analyse de patterns récurrents ---
@tool
def identify_recurrent_patterns_tool(feedbacks: List[str]) -> PatternAnalysisResult:
    """
    Analyse une liste de feedbacks pour identifier les patterns ou thèmes récurrents grâce à un LLM Gemini.
    """
    # 1. Initialisation du parser de sortie
    output_parser = PydanticOutputParser(pydantic_object=PatternAnalysisResult)

    # 2. Initialisation du modèle LLM Gemini
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )

    # 3. Création du prompt template
    prompt = PromptTemplate(
        template="""
        Vous êtes un assistant expert en analyse de feedback utilisateur. Votre tâche est d'identifier les patterns ou thèmes récurrents dans la liste suivante de feedbacks :
        ---
        {feedbacks}
        ---
        Listez les patterns ou thèmes récurrents que vous observez, sous forme de phrases courtes et explicites. 
        
        Retournez uniquement la liste au format JSON suivant :
        {format_instructions}
        """,
        input_variables=["feedbacks"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    # 4. Création de la chaîne d'analyse
    chain = prompt | llm | output_parser

    # 5. Lancement de l'identification
    print("--- Lancement de l'identification des patterns récurrents ---")
    result = chain.invoke({"feedbacks": feedbacks})
    print("--- Identification terminée ---")
    return result