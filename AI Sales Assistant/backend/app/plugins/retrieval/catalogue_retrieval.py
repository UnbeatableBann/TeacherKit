from typing import Any, Dict

from app.plugins.base import PluginBase, PluginContext, SessionState
from app.services.knowledge_retrieval import format_rag_context, retrieve_knowledge_context


class CatalogueRetrievalPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        reqs = state.requirements
        
        # Build semantic search query based on requirements
        search_parts = []
        if reqs.category:
            search_parts.append(reqs.category)
        if reqs.features_wanted:
            search_parts.extend(reqs.features_wanted)
        if reqs.preferences:
            search_parts.extend(reqs.preferences)
            
        search_text = " ".join(search_parts)
        if not search_text.strip():
            # fallback to last message
            if state.messages:
                search_text = state.messages[-1].content
            else:
                return {"retrieved_context_text": ""}
                
        # Document-centric Hybrid Retrieval
        contexts = await retrieve_knowledge_context(
            query=search_text,
            tenant_id=context.tenant_id,
            db=context.db,
            top_k=5
        )
        
        rag_text = format_rag_context(contexts)
        
        return {"retrieved_context_text": rag_text}
