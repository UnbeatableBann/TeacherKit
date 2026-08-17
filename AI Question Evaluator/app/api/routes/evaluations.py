from fastapi import APIRouter

from app.domain.models.requests import EvaluationRequest, EvaluationResponse
from app.engine.registry import get_plugin

router = APIRouter(tags=["evaluations"])


@router.post("/evaluations", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    return get_plugin(request.question.subject).evaluate(request)
