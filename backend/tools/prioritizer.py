import json
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from backend.core.config import GEMINI_API_KEY, MODEL_NAME


# --- Schémas de données ---
class FeatureToPrioritize(BaseModel):
    """
    Représente une fonctionnalité candidate à prioriser.
    Optionnellement, `score_details` permet de pré-renseigner certains sous-scores RICE.
    """
    name: str = Field(description="Titre court et explicite de la fonctionnalité.")
    description: str = Field(description="Description détaillée du besoin utilisateur et du contexte.")
    score_details: str | None = Field(default=None, description="Sous-scores déjà connus (ex. 'reach=60; effort=3').")
    category: str | None = Field(default=None, description="Catégorie de la fonctionnalité : 'bug', 'feature' ou 'comment'.")


class PrioritizedFeature(BaseModel):
    """
    Résultat de la priorisation d'une fonctionnalité, compatible avec RICE, MoSCoW ou tout autre framework.
    """
    feature_name: str = Field(description="Nom de la fonctionnalité priorisée.")
    score: str | None = Field(default=None, description="Scores intermédiaires et justifications sous forme de texte (reach, impact, etc.).")
    final_score: float | None = Field(default=None, description="Score agrégé calculé par le framework, si applicable.")
    qualitative_rank: str | None = Field(default=None, description="Label qualitatif de priorité (Must/Should/etc.).")
    custom: Dict[str, Any] | None = Field(default=None, description="Métriques spécifiques au framework (WSJF, CoD, etc.).")
    justification: str = Field(description="Justification détaillée du classement ou du score.")


class PrioritizationResult(BaseModel):
    """
    Liste des fonctionnalités avec leur priorisation.
    """
    features: List[PrioritizedFeature] = Field(description="Liste des fonctionnalités priorisées.")


# --- Outil de priorisation des fonctionnalités ---
@tool
def prioritize_features_tool(features: List[FeatureToPrioritize], framework: str = 'RICE') -> PrioritizationResult:
    """
    Score et priorise une liste de fonctionnalités selon un framework spécifié (RICE, MoSCoW, etc.).
    """
    # 1. Initialisation du parser de sortie
    output_parser = PydanticOutputParser(pydantic_object=PrioritizationResult)

    # 2. Initialisation du modèle LLM Gemini
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=GEMINI_API_KEY
    )

    # 3. Conversion des fonctionnalités en JSON
    features_json = json.dumps([f.model_dump() for f in features], ensure_ascii=False)

    # 4. Création du prompt template
    prompt = PromptTemplate(
        template="""
        Vous êtes un assistant expert Product Owner. Vous devez appliquer le framework **{framework}** pour prioriser les fonctionnalités. Votre tâche est de **classer et scorer** les fonctionnalités ci‑dessous selon le framework demandé.

        Fonctionnalités (JSON) :
        Les champs optionnels `score_details` contiennent parfois des valeurs déjà fournies (reach, impact, etc.). **Utilise ces valeurs telles quelles** et ne les ré‑estime pas. Complète uniquement les sous‑scores manquants.

        Features :
        {features}

        Règles :
        - Si le framework est RICE → dans le champ 'score', fournis une chaîne de caractères listant chaque sous-score (reach, impact, confidence, effort) suivi d'une justification textuelle pour chacun, par exemple :
          "reach=60 : Justification du reach. impact=8 : Justification de l'impact. confidence=0.9 : Justification de la confiance. effort=3 : Justification de l'effort."
        - Si le framework est MoSCoW → mets Must/Should/Could/Won't dans qualitative_rank et mets les champs numériques à 0.
        - Pour tout autre framework :
            - Renseigne qualitative_rank s'il y a un label (ex. High/Med/Low).
            - Place n'importe quelle métrique spécifique (ex. wsjf, cost_of_delay, value_score, risk) dans custom.
            - Laisse les champs inutilisés à null.

        Retourne strictement la sortie au format JSON suivant :
        {format_instructions}
        """,
        input_variables=["framework", "features"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    # 5. Création de la chaîne d'analyse
    chain = prompt | llm | output_parser

    # 6. Lancement de la priorisation
    print("--- Lancement de la priorisation des fonctionnalités ---")
    result = chain.invoke({"framework": framework, "features": features_json})
    print("--- Priorisation terminée ---")
    return result
