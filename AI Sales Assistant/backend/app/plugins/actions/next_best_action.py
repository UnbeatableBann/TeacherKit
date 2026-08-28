from typing import Any, Dict

from app.plugins.base import PluginBase, PluginContext, SessionState


class NextBestActionPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        unanswered = context.plugin_data.get("qa_result", {}).get("unanswerable_questions", [])
        retrieved = context.plugin_data.get("retrieved_products", [])
        
        action = "continue_conversation"
        reason = "Awaiting customer requirements"
        
        if len(unanswered) > 0:
            action = "escalate"
            reason = "Customer asked questions that cannot be answered from the catalogue."
        elif len(state.objections) > 0 and any(o.status == "unresolved" for o in state.objections):
            action = "address_objection"
            reason = "Customer has unresolved objections."
        elif state.requirements.budget_min is None and state.requirements.budget_max is None:
            action = "ask_budget"
            reason = "Budget is not yet identified."
        elif len(retrieved) == 0 and len(state.requirements.features_wanted) > 0:
            action = "clarify_requirements"
            reason = "No products matched the current requirements."
        elif len(context.plugin_data.get("validated_recommendations", [])) > 0:
            action = "propose_recommendations"
            reason = "Recommendations are ready to be presented."
            
        return {
            "next_best_action": {
                "action": action,
                "reason": reason
            }
        }
