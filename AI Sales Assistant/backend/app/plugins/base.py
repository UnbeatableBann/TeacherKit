from typing import Any, Dict, List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.domain import (
    ObjectionSchema,
    RecommendationSchema,
    RequirementSchema,
)


class SessionState(BaseModel):
    conversation_id: str
    tenant_id: str = "default_tenant" # Could be fetched from customer
    history: List[Dict[str, str]] = [] # list of {"role": "...", "content": "..."}
    requirements: RequirementSchema = RequirementSchema()
    objections: List[ObjectionSchema] = []
    recommendations_shown: List[RecommendationSchema] = []
    summary: str = ""
    lead_score: int = 0
    
from dataclasses import dataclass

@dataclass
class PluginContext:
    db: AsyncSession
    new_message: str
    plugin_data: Dict[str, Any] = None

class PluginBase:
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        raise NotImplementedError
