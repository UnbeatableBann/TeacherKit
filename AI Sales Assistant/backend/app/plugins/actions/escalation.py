from typing import Any, Dict

from app.plugins.base import PluginBase, PluginContext, SessionState


class EscalationPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        nba = context.plugin_data.get("next_best_action", {})
        action = nba.get("action")
        
        triggered = False
        reason = None
        
        if action == "escalate":
            triggered = True
            reason = nba.get("reason", "Automatic escalation trigger met.")
            
        # Optional: other rules like 3 unresolved objections, etc.
        
        return {
            "escalation": {
                "triggered": triggered,
                "reason": reason
            }
        }
