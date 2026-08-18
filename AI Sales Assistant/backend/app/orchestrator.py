from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.base import PluginContext, SessionState
from app.plugins.catalogue_retrieval import CatalogueRetrievalPlugin
from app.plugins.conversation_summary import ConversationSummaryPlugin
from app.plugins.escalation import EscalationPlugin
from app.plugins.grounding_validator import GroundingValidatorPlugin
from app.plugins.intent_extraction import IntentExtractionPlugin
from app.plugins.lead_scoring import LeadScoringPlugin
from app.plugins.next_best_action import NextBestActionPlugin
from app.plugins.objection_handling import ObjectionHandlingPlugin
from app.plugins.qa import QAPlugin
from app.plugins.recommendation import RecommendationPlugin
from app.schemas.domain import MessageCreate, OrchestratorResponse


# Orchestrator
async def load_session_state(conversation_id: str, db: AsyncSession) -> SessionState:
    # Dummy load logic - should load from DB
    return SessionState(conversation_id=conversation_id)

async def save_session_state(state: SessionState, db: AsyncSession):
    # Dummy save logic - should update DB
    pass

async def run_orchestrator(conversation_id: str, payload: MessageCreate, db: AsyncSession) -> OrchestratorResponse:
    state = await load_session_state(conversation_id, db)
    context = PluginContext(db=db, new_message=payload.customer_message or "")
    
    # Store shared data between plugins
    context.plugin_data = {}
    
    # Run pipeline
    intent_res = await IntentExtractionPlugin().run(state, context)
    context.plugin_data.update(intent_res)
    
    retrieval_res = await CatalogueRetrievalPlugin().run(state, context)
    context.plugin_data.update(retrieval_res)
    
    rec_res = await RecommendationPlugin().run(state, context)
    context.plugin_data.update(rec_res)
    
    val_res = await GroundingValidatorPlugin().run(state, context)
    context.plugin_data.update(val_res)
    
    obj_res = await ObjectionHandlingPlugin().run(state, context)
    context.plugin_data.update(obj_res)
    
    qa_res = await QAPlugin().run(state, context)
    context.plugin_data["qa_result"] = qa_res
    
    score_res = await LeadScoringPlugin().run(state, context)
    context.plugin_data.update(score_res)
    
    nba_res = await NextBestActionPlugin().run(state, context)
    context.plugin_data.update(nba_res)
    
    sum_res = await ConversationSummaryPlugin().run(state, context)
    context.plugin_data.update(sum_res)
    
    esc_res = await EscalationPlugin().run(state, context)
    context.plugin_data.update(esc_res)
    
    # Persist state
    await save_session_state(state, db)
    
    # Build response
    return OrchestratorResponse(
        intent=intent_res.get("intent"),
        requirements=state.requirements,
        objections=state.objections,
        recommendations=val_res.get("validated_recommendations", []),
        answered_questions=qa_res.get("answered_questions", []),
        unanswerable_questions=qa_res.get("unanswerable_questions", []),
        lead_score=score_res.get("lead_score"),
        next_best_action=nba_res.get("next_best_action"),
        conversation_summary=sum_res.get("conversation_summary"),
        escalation=esc_res.get("escalation")
    )
