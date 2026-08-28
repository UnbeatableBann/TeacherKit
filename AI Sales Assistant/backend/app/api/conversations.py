# from app.orchestrator import run_orchestrator
# from app.plugins.follow_up_generator import generate_follow_up
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.domain import (
    ConversationStateResponse,
    MessageCreate,
    OrchestratorResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateConversationRequest(BaseModel):
    customer_name: str
    channel: str = "web"


@router.post("")
async def create_conversation(
    payload: CreateConversationRequest, db: AsyncSession = Depends(get_db)
):
    from app.models.domain import Conversation, Customer, LeadScore

    # Normally we'd look up customer or tenant info from auth
    # Create dummy customer
    customer = Customer(
        tenant_id="default_tenant", name=payload.customer_name, contact_info="unknown@example.com"
    )
    db.add(customer)
    await db.flush()

    conv = Conversation(customer_id=customer.id, channel=payload.channel, status="active")
    db.add(conv)
    await db.flush()

    lead_score = LeadScore(
        conversation_id=conv.id, score=50, breakdown={"reason": "New conversation created"}
    )
    db.add(lead_score)
    await db.commit()

    return {"conversation_id": conv.id}


@router.post("/{conversation_id}/messages", response_model=OrchestratorResponse)
async def process_message(
    conversation_id: str, payload: MessageCreate, db: AsyncSession = Depends(get_db)
):
    from app.orchestrator import run_orchestrator

    try:
        import google.genai.errors

        result = await run_orchestrator(conversation_id, payload, db)
    except ValueError as e:
        logger.error(f"ValueError in orchestrator: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except google.genai.errors.ClientError as e:
        raise HTTPException(status_code=429, detail=f"Gemini API rate limit exceeded: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    return result


@router.get("/{conversation_id}", response_model=ConversationStateResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    # Retrieve current session state
    # TODO: query db for Conversation, ExtractedRequirement, Recommendations, etc.
    from app.models.domain import Conversation, ExtractedRequirement, LeadScore, Recommendation

    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    req_res = await db.execute(
        select(ExtractedRequirement).where(ExtractedRequirement.conversation_id == conversation_id)
    )
    req = req_res.scalar_one_or_none()

    lead_res = await db.execute(
        select(LeadScore).where(LeadScore.conversation_id == conversation_id)
    )
    lead = lead_res.scalar_one_or_none()

    rec_res = await db.execute(
        select(Recommendation).where(Recommendation.conversation_id == conversation_id)
    )
    recs = rec_res.scalars().all()

    # Needs proper serialization based on Pydantic schemas, but returning dicts/models for now
    return {
        "id": conv.id,
        "requirements": req or {"features_wanted": [], "preferences": []},
        "summary": "Summary text",  # From state
        "lead_score": lead or {"score": 0, "breakdown": {}},
        "recommendations_shown": recs,
    }


@router.post("/{conversation_id}/follow-up")
async def generate_followup(conversation_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.domain import FollowUp

    # Fetch the latest draft for this conversation
    stmt = (
        select(FollowUp)
        .where(FollowUp.conversation_id == conversation_id, FollowUp.sent_status == "draft")
        .order_by(FollowUp.id.desc())
    )

    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    if draft:
        return {"draft_text": draft.draft_text}
    else:
        return {"draft_text": "No follow-up draft is available yet."}
