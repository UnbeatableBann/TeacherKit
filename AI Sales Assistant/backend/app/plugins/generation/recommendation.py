from typing import Any, Dict

from app.llm_client import generate_structured
from app.plugins.base import PluginBase, PluginContext, SessionState


class RecommendationPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        retrieved_context_text = context.plugin_data.get("retrieved_context_text", "")
        
        if not retrieved_context_text.strip():
            return {"recommendations": []}
            
        prompt = f"""
Customer Requirements:
{state.requirements.model_dump_json()}

Knowledge Base Context (DO NOT INVENT ANY PRODUCTS OR SPECS):
{retrieved_context_text}

Generate up to 3 recommendations based ONLY on the provided Knowledge Base Context.
Explain why each recommendation fits.

Return JSON in this format:
{{
    "recommendations": [
        {{
            "product_id": "extract a unique id or use the product name",
            "name": "product or service name from context",
            "price": 0.0,
            "matched_features": ["list of features"],
            "reasoning": "explanation",
            "confidence": 0.9
        }}
    ]
}}
"""
        system_prompt = "You are a sales recommender. Never invent products or facts. Only use the provided Knowledge Base Context."
        result = await generate_structured(prompt, system_prompt)
        
        recs = result.get("recommendations", [])
        return {"recommendations": recs}
