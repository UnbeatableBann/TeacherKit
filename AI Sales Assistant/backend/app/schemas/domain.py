from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    customer_message: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class RequirementSchema(BaseModel):
    category: Optional[str] = None
    features_wanted: List[str] = Field(default_factory=list)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferences: List[str] = Field(default_factory=list)
    urgency: Optional[str] = None

class ObjectionSchema(BaseModel):
    type: str
    text: str
    status: str

class RecommendationSchema(BaseModel):
    product_id: str
    name: str
    price: float
    matched_features: List[str]
    reasoning: str
    confidence: float

class AnsweredQuestionSchema(BaseModel):
    question: str
    answer: str
    source_product_ids: List[str]

class LeadScoreSchema(BaseModel):
    score: int
    breakdown: Dict[str, Any]

class NextBestActionSchema(BaseModel):
    action: str
    reason: str

class EscalationSchema(BaseModel):
    triggered: bool
    reason: Optional[str] = None

class OrchestratorResponse(BaseModel):
    intent: Optional[str] = None
    requirements: RequirementSchema
    objections: List[ObjectionSchema]
    recommendations: List[RecommendationSchema]
    answered_questions: List[AnsweredQuestionSchema]
    unanswerable_questions: List[str]
    lead_score: LeadScoreSchema
    next_best_action: NextBestActionSchema
    conversation_summary: Optional[str] = None
    escalation: EscalationSchema

class FollowUpRequest(BaseModel):
    conversation_id: str

class ConversationStateResponse(BaseModel):
    id: str
    requirements: RequirementSchema
    summary: Optional[str] = None
    lead_score: Optional[LeadScoreSchema] = None
    recommendations_shown: List[RecommendationSchema] = Field(default_factory=list)
