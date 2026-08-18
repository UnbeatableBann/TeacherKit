from typing import Any, Dict

from sqlalchemy import select

from app.embeddings_client import get_embedding
from app.models.domain import Product, ProductEmbedding
from app.plugins.base import PluginBase, PluginContext, SessionState


class CatalogueRetrievalPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> Dict[str, Any]:
        reqs = state.requirements
        
        # Build strict filters
        query = select(Product)
        query = query.where(Product.tenant_id == state.tenant_id)
        
        if reqs.category:
            query = query.where(Product.category == reqs.category)
        if reqs.budget_min is not None:
            query = query.where(Product.price >= reqs.budget_min)
        if reqs.budget_max is not None:
            query = query.where(Product.price <= reqs.budget_max)
            
        result = await context.db.execute(query)
        candidates = result.scalars().all()
        
        if not candidates:
            return {"retrieved_products": []}
            
        # Vector search if we have textual features/preferences
        search_text = " ".join(reqs.features_wanted + reqs.preferences)
        if not search_text.strip():
            # No semantic search needed, just return filtered candidates (up to 5)
            return {"retrieved_products": [self._format_product(c) for c in candidates[:5]]}
            
        # Semantic Ranking
        query_emb = await get_embedding(search_text)
        
        candidate_ids = [c.id for c in candidates]
        emb_query = select(ProductEmbedding).where(ProductEmbedding.product_id.in_(candidate_ids))
        # Use pgvector cosine distance: embedding.cosine_distance(query_emb)
        emb_query = emb_query.order_by(ProductEmbedding.embedding.cosine_distance(query_emb)).limit(5)
        
        emb_result = await context.db.execute(emb_query)
        ranked_emb_records = emb_result.scalars().all()
        
        # Map back to products
        candidate_map = {c.id: c for c in candidates}
        retrieved_products = [self._format_product(candidate_map[r.product_id]) for r in ranked_emb_records]
        
        return {"retrieved_products": retrieved_products}

    def _format_product(self, p: Product) -> Dict[str, Any]:
        return {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "currency": p.currency,
            "specs": p.specs,
            "description": p.description,
            "stock_status": p.stock_status
        }
