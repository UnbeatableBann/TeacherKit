import json
from typing import Any, Dict

from app.llm_client import generate_structured
from app.plugins.base import PluginBase, PluginContext, SessionState


class QAPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        retrieved_products = context.plugin_data.get("retrieved_products", [])
        
        prompt = f"""
Customer Message:
{context.new_message}

Candidate Products:
{json.dumps(retrieved_products)}

Does the customer ask a question? If so, answer it ONLY using the Candidate Products data.
If the answer is not in the data, add the question to 'unanswerable_questions' and do NOT guess.

Format:
{{
    "answered_questions": [
        {{
            "question": "string",
            "answer": "string",
            "source_product_ids": ["string"]
        }}
    ],
    "unanswerable_questions": ["string"]
}}
"""
        system_prompt = "You answer questions strictly from provided data. Never guess."
        result = await generate_structured(prompt, system_prompt)
        
        return {
            "answered_questions": result.get("answered_questions", []),
            "unanswerable_questions": result.get("unanswerable_questions", [])
        }
