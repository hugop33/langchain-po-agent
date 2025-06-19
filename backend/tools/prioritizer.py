import json
from typing import List, Dict
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from backend.core.config import GEMINI_API_KEY, MODEL_NAME


# --- Schémas de Données pour la Priorisation ---
class FeatureToPrioritize(BaseModel):
    """
    Représente une feature candidate à prioriser.
    """
    name: str = Field(description="Titre court de la fonctionnalité.")
    description: str = Field(description="Description détaillée de la fonctionnalité.")

class PrioritizedFeature(BaseModel):
    """
    Résultat de la priorisation pour une feature.
    """
    feature_name: str = Field(description="Le nom de la fonctionnalité priorisée.")
    score: Dict[str, float] = Field(description="Scores détaillés selon le framework (e.g., reach, impact, confidence, effort).")
    final_score: float = Field(description="Score agrégé pour le classement final.")
    justification: str = Field(description="Explication de la note attribuée.")

class PrioritizationResult(BaseModel):
    """
    Liste des fonctionnalités avec leurs priorisations.
    """
    features: List[PrioritizedFeature] = Field(
        description="Liste des fonctionnalités avec score détaillé et justification.",
        default_factory=list
    )

@tool
def prioritize_features_tool(features: List[FeatureToPrioritize], framework: str = 'RICE') -> PrioritizationResult:
    """
    Scores and prioritizes a list of features using a specified framework like RICE or MoSCoW.
    """
    # Préparation du parser de sortie
    output_parser = PydanticOutputParser(pydantic_object=PrioritizationResult)

    # Initialisation du LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=GEMINI_API_KEY
    )

    # Conversion des features en JSON
    features_json = json.dumps([f.model_dump() for f in features], ensure_ascii=False)

    # Construction du prompt
    prompt = PromptTemplate(
        template="""
        Vous êtes un assistant expert en gestion de produit. Appliquez le framework {framework} pour prioriser
        la liste suivante de fonctionnalités (format JSON) :
        {features}

        Pour chaque fonctionnalité, calculez et expliquez:
        - reach (portée)
        - impact
        - confidence (confiance)
        - effort
        Puis agréegez ces sous-scores en un final_score numérique selon le framework {framework}.

        Retournez la sortie strictement au format JSON conforme à ces instructions :
        {format_instructions}
        """,
        input_variables=["framework", "features"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    # Chaîne d'exécution
    chain = prompt | llm | output_parser

    # Exécution et parsing
    print("--- Lancement de la priorisation des features ---")
    result = chain.invoke({"framework": framework, "features": features_json})
    print("--- Priorisation terminée. ---")
    return result
