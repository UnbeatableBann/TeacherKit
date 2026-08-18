import json
from typing import Any, Dict

from app.llm_client import generate_structured
from app.plugins.base import PluginBase, PluginContext, SessionState


class RecommendationPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        retrieved_products = context.plugin_data.get("retrieved_products", [])
        
        if not retrieved_products:
            return {"recommendations": []}
            
        prompt = f"""
Customer Requirements:
{state.requirements.model_dump_json()}

Candidate Products from Catalogue (DO NOT INVENT ANY PRODUCTS OR SPECS):
{json.dumps(retrieved_products)}

Generate up to 3 recommendations based ONLY on the candidates provided.
Explain why each recommendation fits.

Return JSON in this format:
{{
    "recommendations": [
        {{
            "product_id": "id from candidates",
            "name": "name from candidates",
            "price": 0.0,
            "matched_features": ["list of features"],
            "reasoning": "explanation",
            "confidence": 0.9
        }}
    ]
}}
"""
        system_prompt = "You are a sales recommender. Never invent products or facts. Only use the provided candidates."
        result = await generate_structured(prompt, system_prompt)
        
        recs = result.get("recommendations", [])
        return {"recommendations": recs}
