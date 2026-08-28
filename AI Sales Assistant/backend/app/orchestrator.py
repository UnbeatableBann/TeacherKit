import logging
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.domain import (
    MessageCreate, 
    OrchestratorResponse,
    RequirementSchema,
    ObjectionSchema,
    RecommendationSchema,
    AnsweredQuestionSchema,
    LeadScoreSchema,
    NextBestActionSchema,
    EscalationSchema
)
from app.models.domain import Conversation, Message, ExtractedRequirement, Recommendation, FollowUp
from app.services.follow_up_service import (
    normalize_input, 
    analyze_customer_input, 
    generate_follow_up
)
from app.services.knowledge_retrieval import retrieve_knowledge_context, format_rag_context

logger = logging.getLogger(__name__)

async def run_orchestrator(conversation_id: str, payload: MessageCreate, db: AsyncSession) -> OrchestratorResponse:
    # 1. Normalize Input
    # We treat customer_message as the raw input block which could be a single message or a conversation
    raw_text = payload.customer_message or ""
    try:
        normalized_input = normalize_input(raw_text)
    except ValueError as e:
        # Fallback to an empty representation if validation fails, although Pydantic usually stops it
        logger.error(f"Failed to normalize input: {e}")
        raise

    # Persist the messages
    for msg in normalized_input.messages:
        db_message = Message(
            conversation_id=conversation_id,
            role=msg.role,
            content=msg.content
        )
        db.add(db_message)

    # 2. Analyze current input
    analysis = await analyze_customer_input(normalized_input)
    
    # 3. Decide if recommendation is needed & Retrieve Knowledge Base
    rag_context_str = ""
    if analysis.recommendation_needed:
        # Build query from requirements + intent
        query_parts = []
        if analysis.intent:
            query_parts.append(analysis.intent)
        if analysis.requirements:
            query_parts.extend(analysis.requirements)
        if analysis.budget and analysis.budget.max:
            query_parts.append(f"under {analysis.budget.max}")
        query = " ".join(query_parts)
        
        # Hardcoding a tenant_id for V1 (should come from auth)
        tenant_id = "default_tenant" 
        contexts = await retrieve_knowledge_context(query, tenant_id, db, top_k=5)
        rag_context_str = format_rag_context(contexts)

    # 4. Generate Follow-up
    # We always generate follow-up even if recommendation_needed is False
    generation_result = await generate_follow_up(
        normalized_input=normalized_input,
        analysis=analysis,
        rag_context=rag_context_str
    )

    # 5. Persist Everything
    # Persist Requirements
    db_req = await db.execute(select(ExtractedRequirement).where(ExtractedRequirement.conversation_id == conversation_id))
    db_req = db_req.scalar_one_or_none()
    
    budget_min = analysis.budget.min if analysis.budget else None
    budget_max = analysis.budget.max if analysis.budget else None
    
    if not db_req:
        db_req = ExtractedRequirement(
            conversation_id=conversation_id,
            category=analysis.intent,
            features_wanted=analysis.requirements,
            budget_min=budget_min,
            budget_max=budget_max,
            preferences=analysis.preferences
        )
        db.add(db_req)
    else:
        db_req.category = analysis.intent
        db_req.features_wanted = analysis.requirements
        db_req.budget_min = budget_min
        db_req.budget_max = budget_max
        db_req.preferences = analysis.preferences

    # Persist Recommendations
    for rec in generation_result.recommendations:
        db_rec = Recommendation(
            conversation_id=conversation_id,
            name=rec.name,
            reasoning=rec.reason,
            sources=rec.sources
        )
        db.add(db_rec)
        
    # Persist FollowUp Draft
    db_followup = FollowUp(
        conversation_id=conversation_id,
        draft_text=generation_result.follow_up_message,
        sent_status="draft"
    )
    db.add(db_followup)
    
    await db.commit()

    # 6. Format Response using exact Frontend Contract
    # Note: We satisfy the schema but leave out-of-scope fields dummy/empty
    
    # Format requirements
    req_schema = RequirementSchema(
        category=analysis.intent,
        features_wanted=analysis.requirements,
        budget_min=budget_min,
        budget_max=budget_max,
        preferences=analysis.preferences
    )
    
    # Format objections
    obj_schemas = [ObjectionSchema(type="general", text=obj, status="unresolved") for obj in analysis.objections]
    
    # Format recommendations
    rec_schemas = []
    for rec in generation_result.recommendations:
        rec_schemas.append(RecommendationSchema(
            name=rec.name,
            reasoning=rec.reason,
            sources=rec.sources
        ))
        
    return OrchestratorResponse(
        intent=analysis.intent,
        requirements=req_schema,
        objections=obj_schemas,
        recommendations=rec_schemas,
        answered_questions=[],  # Out of scope for this V1
        unanswerable_questions=[],
        lead_score=LeadScoreSchema(score=0, breakdown={"reason": "Not implemented in V1"}),
        next_best_action=NextBestActionSchema(action="Send Follow-up", reason="Draft is ready"),
        conversation_summary="Not implemented in V1",
        escalation=EscalationSchema(triggered=False)
    )

async def load_session_state(conversation_id: str, db: AsyncSession):
    pass

async def save_session_state(state, db: AsyncSession):
    pass
