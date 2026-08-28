from typing import Any, Dict

from app.plugins.base import PluginBase, PluginContext, SessionState


class LeadScoringPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        score = 0
        breakdown = {}
        
        # Rules-based scoring
        if state.requirements.budget_max is not None:
            score += 20
            breakdown["budget_provided"] = 20
            
        if len(state.requirements.features_wanted) > 0:
            score += 10
            breakdown["features_identified"] = 10
            
        if state.requirements.urgency and state.requirements.urgency.lower() in ["high", "immediate", "asap"]:
            score += 30
            breakdown["high_urgency"] = 30
            
        if len(state.objections) == 0 and len(state.requirements.features_wanted) > 0:
            score += 10
            breakdown["no_objections"] = 10
            
        state.lead_score = score
        return {"lead_score": {"total": score, "breakdown": breakdown}}
