from typing import Any, Dict

from sqlalchemy import select

from app.models.domain import PluginExecutionLog, Product
from app.plugins.base import PluginBase, PluginContext, SessionState
from app.schemas.domain import RecommendationSchema


class GroundingValidatorPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        recs = context.plugin_data.get("recommendations", [])
        if not recs:
            return {"validated_recommendations": []}
            
        validated_recs = []
        validation_failures = []
        
        for rec in recs:
            # Re-fetch product to be absolutely sure
            product_id = rec.get("product_id")
            result = await context.db.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()
            
            if not product:
                validation_failures.append({"rec": rec, "reason": "product_id not in DB"})
                continue
                
            # Verify basic facts
            if rec.get("name") != product.name:
                validation_failures.append({"rec": rec, "reason": "Name mismatch"})
                continue
                
            if float(rec.get("price")) != float(product.price):
                validation_failures.append({"rec": rec, "reason": "Price mismatch"})
                continue
                
            # Assume matched if name and price matches; more rigorous spec checking could be added
            rec_obj = RecommendationSchema(**rec)
            validated_recs.append(rec_obj)
            
        # Log failures
        if validation_failures:
            log_entry = PluginExecutionLog(
                conversation_id=state.conversation_id,
                plugin_name="GroundingValidator",
                input_snapshot={"recommendations": recs},
                validation_result={"failures": validation_failures},
                latency_ms=0
            )
            context.db.add(log_entry)
            
        return {"validated_recommendations": [r.model_dump() for r in validated_recs]}
