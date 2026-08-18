from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Conversation, Customer, LeadScore

router = APIRouter()

@router.get("/")
async def list_leads(
    tenant_id: str = None,
    sort: str = "score",
    db: AsyncSession = Depends(get_db)
):
    # Simplified query
    query = select(Conversation, LeadScore, Customer).join(LeadScore).join(Customer)
    if tenant_id:
        query = query.where(Customer.tenant_id == tenant_id)
        
    if sort == "score":
        query = query.order_by(LeadScore.score.desc())
        
    result = await db.execute(query)
    leads = result.all()
    
    # Return formatted list
    return [
        {
            "conversation_id": conv.id,
            "customer_name": cust.name,
            "score": ls.score,
            "last_activity": conv.last_activity_at
        }
        for conv, ls, cust in leads
    ]
