
from app.llm_client import generate_completion
from app.plugins.base import PluginBase, PluginContext, SessionState
from app.services.knowledge_retrieval import format_rag_context, retrieve_knowledge_context


class FollowUpGeneratorPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> str:
        # V1 generation rule: use current message, current analysis, and RAG context
        current_msg = state.messages[-1].content if state.messages else ""
        
        # Generate search query based on requirements/message
        search_query = current_msg
        
        # Retrieve context
        contexts = await retrieve_knowledge_context(
            query=search_query,
            tenant_id=context.tenant_id,
            db=context.db,
            top_k=5
        )
        
        rag_text = format_rag_context(contexts)
        
        prompt = f"""
Current Customer Message:
"{current_msg}"

Current Message Analysis (Requirements):
{state.requirements.model_dump_json()}

Knowledge Base Context:
{rag_text}

Write a professional follow-up email/message to the customer addressing their needs based on the Knowledge Base Context. 
IMPORTANT: 
- Do NOT invent new prices, products, specifications, or policies.
- If the knowledge base does not contain sufficient information, state that explicitly instead of hallucinating.
- Do NOT use previous conversation history or old stored summaries for this generation.
"""
        system_prompt = "You are a professional sales agent drafting a follow-up email. Only use confirmed data from the knowledge base context."
        draft = await generate_completion(prompt, system_prompt)
        return draft
