from typing import Optional, List
from pydantic import BaseModel, Field, RootModel
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from backend.core.config import GEMINI_API_KEY, MODEL_NAME

class FeedbackItem(BaseModel):
    type: str = Field(description="Le type de feedback : 'feature', 'bug', ou 'comment'.")
    summary: str = Field(description="Un résumé concis du feedback en une phrase.")
    feature_request: Optional[str] = Field(description="La description de la fonctionnalité demandée, si applicable.")

class FeedbackList(RootModel[List[FeedbackItem]]):
    pass

def analyze_feedback(feedbacks_as_str: str) -> list[dict]:
    """
    Outil d'analyse de feedbacks utilisateurs pour Product Owner.
    À utiliser lorsque tu veux extraire automatiquement les demandes de fonctionnalités, bugs ou commentaires à partir d'une liste de feedbacks bruts (emails, tickets, etc.).
    Entrée : une chaîne de caractères contenant plusieurs feedbacks utilisateurs (un par ligne ou séparés par un délimiteur).
    Retour : une liste de dictionnaires structurés avec type, résumé et demande de fonctionnalité éventuelle.
    """
    parser = PydanticOutputParser(pydantic_object=FeedbackList)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
        template=(
            "Tu es un assistant pour Product Owner. "
            "Tu analyses des feedbacks utilisateurs et tu extrais pour chacun : le type ('feature', 'bug', 'comment'), "
            "un résumé concis, et la description de la fonctionnalité demandée si applicable.\n"
            "Voici des feedbacks utilisateurs (un par ligne) :\n{feedbacks}\n\n"
            "Respecte scrupuleusement ce format pour chaque feedback :\n{format_instructions}"
        ),
        input_variables=["feedbacks", "format_instructions"]
    )
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.1
    )
    chain = prompt | llm | parser

    print("Analyse des feedbacks en cours...")

    result = chain.invoke({"feedbacks": feedbacks_as_str, "format_instructions": format_instructions})
    return [item.dict() for item in result.root] 