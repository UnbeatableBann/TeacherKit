from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.domain import (
    ConversationStateResponse,
    MessageCreate,
    OrchestratorResponse,
)

# from app.orchestrator import run_orchestrator
# from app.plugins.follow_up_generator import generate_follow_up

router = APIRouter()

@router.post("/{conversation_id}/messages", response_model=OrchestratorResponse)
async def process_message(
    conversation_id: str, 
    payload: MessageCreate, 
    db: AsyncSession = Depends(get_db)
):
    from app.orchestrator import run_orchestrator
    # Pass off to the orchestrator
    result = await run_orchestrator(conversation_id, payload, db)
    return result

@router.get("/{conversation_id}", response_model=ConversationStateResponse)
async def get_conversation(
    conversation_id: str, 
    db: AsyncSession = Depends(get_db)
):
    # Retrieve current session state
    # TODO: query db for Conversation, ExtractedRequirement, Recommendations, etc.
    from app.models.domain import Conversation, ExtractedRequirement, LeadScore, Recommendation
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    req_res = await db.execute(select(ExtractedRequirement).where(ExtractedRequirement.conversation_id == conversation_id))
    req = req_res.scalar_one_or_none()

    lead_res = await db.execute(select(LeadScore).where(LeadScore.conversation_id == conversation_id))
    lead = lead_res.scalar_one_or_none()

    rec_res = await db.execute(select(Recommendation).where(Recommendation.conversation_id == conversation_id))
    recs = rec_res.scalars().all()
    
    # Needs proper serialization based on Pydantic schemas, but returning dicts/models for now
    return {
        "id": conv.id,
        "requirements": req or {"features_wanted": [], "preferences": []},
        "summary": "Summary text", # From state
        "lead_score": lead or {"total": 0, "breakdown": {}},
        "recommendations_shown": recs
    }

@router.post("/{conversation_id}/follow-up")
async def generate_followup(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    from app.orchestrator import load_session_state
    from app.plugins.generation.follow_up_generator import FollowUpGeneratorPlugin
    
    state = await load_session_state(conversation_id, db)
    plugin = FollowUpGeneratorPlugin()
    draft = await plugin.run(state, db)
    
    return {"draft_text": draft}
