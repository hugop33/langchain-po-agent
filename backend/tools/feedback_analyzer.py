from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from backend.core.config import GEMINI_API_KEY, MODEL_NAME


# --- Schémas de Données (Data Schemas) ---
class Feature(BaseModel):
    """
    Représente une seule demande de fonctionnalité extraite d'un feedback.
    """
    name: str = Field(description="Un titre court et descriptif pour la fonctionnalité demandée.")
    description: str = Field(description="Une description détaillée de ce que la fonctionnalité devrait faire, basée sur le feedback.")
    source_feedbacks: List[str] = Field(description="Une liste des phrases exactes du feedback qui justifient cette demande de fonctionnalité.")

class AnalysisResult(BaseModel):
    """
    Le résultat complet de l'analyse, contenant une liste de toutes les fonctionnalités extraites.
    """
    features: List[Feature] = Field(description="Une liste des fonctionnalités extraites du texte de feedback.", default_factory=list)

# --- Définition de l'Outil (Tool Definition) ---
@tool
def analyze_feedback_tool(feedback_text: str) -> AnalysisResult:
    """
    Analyzes raw feedback text (such as emails or comments) to identify recurring themes
    and extract structured feature requests.
    """
    # 1. Initialisation du parser de sortie
    output_parser = PydanticOutputParser(pydantic_object=AnalysisResult)

    # 3. Initialisation du Modèle LLM avec Gemini
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        google_api_key=GEMINI_API_KEY
        )

    # 4. Création du Prompt Template
    prompt = PromptTemplate(
        template="""
        Vous êtes un assistant expert pour un Product Owner. Votre rôle est d'analyser le feedback des utilisateurs
        et d'en extraire des demandes de fonctionnalités claires et exploitables.

        Analysez le feedback suivant :
        ---
        {feedback}
        ---

        Identifiez chaque demande de fonctionnalité distincte. Pour chaque demande, fournissez un nom, une description
        et les extraits exacts du feedback qui la concernent. Ne regroupez que les feedbacks qui parlent
        EXACTEMENT de la même fonctionnalité. Si aucune fonctionnalité n'est mentionnée, retournez une liste vide.

        Retournez la sortie strictement au format JSON conforme à ces instructions :
        {format_instructions}
        """,
        input_variables=["feedback"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    # 5. Création de la Chaîne (Chain)
    chain = prompt | llm | output_parser

    # 6. Invocation de la Chaîne
    print("--- Lancement de l'analyse du feedback ---")
    result = chain.invoke({"feedback": feedback_text})
    print("--- Analyse terminée. ---")
    return result