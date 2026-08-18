from typing import Any, Dict

from app.llm_client import generate_structured
from app.plugins.base import PluginBase, PluginContext, SessionState
from app.schemas.domain import ObjectionSchema


class ObjectionHandlingPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        prompt = f"""
Latest Customer Message:
{context.new_message}

Identify if the customer has an objection (price, feature gap, trust, timing).
If yes, return the objection. If no, return null for type.

Format:
{{
    "type": "string or null",
    "text": "string",
    "status": "unresolved"
}}
"""
        system_prompt = "Identify objections. Return JSON."
        result = await generate_structured(prompt, system_prompt)
        
        obj_type = result.get("type")
        if obj_type:
            objection = ObjectionSchema(
                type=obj_type,
                text=result.get("text", context.new_message),
                status="unresolved"
            )
            state.objections.append(objection)
            return {"objection_detected": True, "objection": objection.model_dump()}
            
        return {"objection_detected": False}
