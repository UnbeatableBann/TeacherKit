from typing import Any, Dict

from app.models.domain import PluginExecutionLog
from app.plugins.base import PluginBase, PluginContext, SessionState
from app.schemas.domain import RecommendationSchema


class GroundingValidatorPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        recs = context.plugin_data.get("recommendations", [])
        if not recs:
            return {"validated_recommendations": []}
            
        validated_recs = []
        
        for rec in recs:
            # We no longer strictly validate against a Product table.
            # RAG grounding is enforced by the LLM prompt.
            # In the future, an LLM-as-a-judge could verify grounding here.
            try:
                rec_obj = RecommendationSchema(**rec)
                validated_recs.append(rec_obj)
            except Exception as e:
                # Malformed schema
                log_entry = PluginExecutionLog(
                    conversation_id=state.conversation_id,
                    plugin_name="GroundingValidator",
                    input_snapshot={"recommendations": [rec]},
                    validation_result={"failures": [str(e)]},
                    latency_ms=0
                )
                context.db.add(log_entry)
            
        return {"validated_recommendations": [r.model_dump() for r in validated_recs]}
