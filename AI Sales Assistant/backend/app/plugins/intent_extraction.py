import json
from typing import Any, Dict

from app.llm_client import generate_structured
from app.plugins.base import PluginBase, PluginContext, SessionState
from app.schemas.domain import RequirementSchema


class IntentExtractionPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        prompt = f"""
Current Requirements:
{state.requirements.model_dump_json()}

Conversation History:
{json.dumps(state.history[-5:])}

Latest Message:
{context.new_message}

Extract the customer's intent from the latest message.
Merge any new requirements or preferences into the existing requirements.
If a budget is explicitly stated, update budget_min/budget_max.
If a preference contradicts an older one, replace it.

Return JSON in this format:
{{
    "intent": "string (e.g. inquiry, purchase, objection, support)",
    "requirements": {{
        "category": "string or null",
        "features_wanted": ["list of strings"],
        "budget_min": "number or null",
        "budget_max": "number or null",
        "preferences": ["list of strings"],
        "urgency": "string or null"
    }}
}}
"""
        system_prompt = "You are a sales assistant intent extraction engine. Strictly merge requirements and output valid JSON."
        result = await generate_structured(prompt, system_prompt)
        
        # Update state
        state.requirements = RequirementSchema(**result.get("requirements", state.requirements.model_dump()))
        
        return {"intent": result.get("intent", "unknown")}
