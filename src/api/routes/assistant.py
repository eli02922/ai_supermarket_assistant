from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from src.rag.llm_client import LLMClient
from src.rag.retriever import RAGRetriever
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

llm_client = LLMClient()
rag_retriever = RAGRetriever()


class QuestionRequest(BaseModel):
    question: str
    context: Optional[List[str]] = None
    include_rag: bool = True


class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    sources: Optional[List[Dict[str, Any]]] = None
    raw_response: Optional[Dict[str, Any]] = None


@router.post("/ask", response_model=AnswerResponse)
async def ask_assistant(request: QuestionRequest) -> AnswerResponse:
    """Ask the AI assistant a question about supermarket data"""
    try:
        if request.include_rag:
            # Retrieve relevant context from RAG
            context = rag_retriever.retrieve(request.question)
        else:
            context = []

        # Get answer from LLM
        response = llm_client.ask(
            question=request.question,
            context=context,
        )
        return AnswerResponse(**response)
    except Exception as e:
        logger.error(f"Assistant query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_insight(
    insight_type: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Get an explanation for an insight"""
    try:
        explanation = llm_client.explain_insight(
            insight_type=insight_type,
            data=data,
        )
        return explanation
    except Exception as e:
        logger.error(f"Insight explanation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights")
async def generate_insights(
    product_id: Optional[str] = None,
    store_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Generate business insights using LLM"""
    try:
        insights = llm_client.generate_insights(
            product_id=product_id,
            store_id=store_id,
        )
        return insights
    except Exception as e:
        logger.error(f"Insight generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))