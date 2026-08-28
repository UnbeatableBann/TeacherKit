from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Escalation

router = APIRouter()

@router.post("/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: str,
    rep_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = update(Escalation).where(Escalation.id == escalation_id).values(
        resolved_at=datetime.now(),
        assigned_rep_id=rep_id
    )
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Escalation not found")
        
    return {"status": "resolved"}
