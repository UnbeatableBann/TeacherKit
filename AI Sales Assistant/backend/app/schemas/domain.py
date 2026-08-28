from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

class MessageCreate(BaseModel):
    customer_message: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

    @model_validator(mode='after')
    def check_exactly_one(self):
        msg = self.customer_message
        hist = self.conversation_history
        
        has_msg = bool(msg and msg.strip())
        has_hist = bool(hist and len(hist) > 0)
        
        if not (has_msg ^ has_hist):
            raise ValueError("Exactly one of customer_message or conversation_history must be provided and not empty.")
            
        if has_hist:
            for item in hist:
                if 'role' not in item or 'content' not in item:
                    raise ValueError("Conversation history items must contain 'role' and 'content' keys.")
                if not item['content'].strip():
                    raise ValueError("Conversation history content cannot be empty.")
        return self

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
    id: str = ""
    name: str
    reasoning: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)

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

from datetime import datetime


class KnowledgeDocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    size: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class KnowledgeDocumentListResponse(BaseModel):
    documents: List[KnowledgeDocumentResponse]

class KnowledgeDocumentUploadResponse(BaseModel):
    document_id: str
    status: str
