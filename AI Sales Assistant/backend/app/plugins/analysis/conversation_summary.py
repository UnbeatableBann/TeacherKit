from typing import Any, Dict

from app.llm_client import generate_completion
from app.plugins.base import PluginBase, PluginContext, SessionState


class ConversationSummaryPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        prompt = f"""
Existing Summary:
{state.summary}

New Message:
{context.new_message}

Update the summary incrementally. Keep it concise.
"""
        system_prompt = "You are a summarizing agent. Update the summary incrementally."
        new_summary = await generate_completion(prompt, system_prompt)
        
        state.summary = new_summary
        return {"conversation_summary": new_summary}
