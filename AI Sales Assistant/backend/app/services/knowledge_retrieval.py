import logging
from typing import List

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings_client import get_embedding
from app.models.domain import KnowledgeChunk, KnowledgeDocument

logger = logging.getLogger(__name__)

class RetrievedContext:
    def __init__(self, chunk: KnowledgeChunk, score: float, doc: KnowledgeDocument):
        self.chunk_id = chunk.id
        self.document_id = doc.id
        self.filename = doc.filename
        self.page_number = chunk.page_number
        self.content = chunk.content
        self.score = score
        self.metadata = chunk.metadata_

async def retrieve_knowledge_context(
    query: str,
    tenant_id: str,
    db: AsyncSession,
    top_k: int = 5,
    similarity_threshold: float = 0.5
) -> List[RetrievedContext]:
    """
    Hybrid search: Semantic search + basic Keyword search fallback.
    Returns the top retrieved contexts formatted for RAG.
    """
    # Generate embedding for query
    query_embedding = await get_embedding(query)
    
    # 1. Semantic Search (Vector)
    # Cosine distance in pgvector is <=
    # Postgres vector '<=>' operator gives distance. Similarity = 1 - distance
    
    # Let's perform a hybrid search using both vector similarity and lexical search (tsvector).
    # Since we are using SQLAlchemy ORM, we can construct the query.
    # To keep it simple, we use raw SQL or SQLAlchemy `text`.
    
    # We join chunks with documents to enforce tenant isolation and status='ready'.
    
    stmt = text("""
        WITH semantic_search AS (
            SELECT 
                c.id as chunk_id,
                1 - (c.embedding <=> :embedding) AS semantic_score
            FROM knowledge_chunks c
            JOIN knowledge_documents d ON c.document_id = d.id
            WHERE d.tenant_id = :tenant_id AND d.status = 'ready'
        ),
        keyword_search AS (
            SELECT 
                c.id as chunk_id,
                ts_rank(to_tsvector('english', c.content), plainto_tsquery('english', :query)) AS keyword_score
            FROM knowledge_chunks c
            JOIN knowledge_documents d ON c.document_id = d.id
            WHERE d.tenant_id = :tenant_id AND d.status = 'ready'
        )
        SELECT 
            c.id as chunk_id,
            COALESCE(s.semantic_score, 0) as semantic_score,
            COALESCE(k.keyword_score, 0) as keyword_score,
            (COALESCE(s.semantic_score, 0) * 0.7 + COALESCE(k.keyword_score, 0) * 0.3) as combined_score
        FROM knowledge_chunks c
        LEFT JOIN semantic_search s ON c.id = s.chunk_id
        LEFT JOIN keyword_search k ON c.id = k.chunk_id
        WHERE (COALESCE(s.semantic_score, 0) * 0.7 + COALESCE(k.keyword_score, 0) * 0.3) > :threshold
        ORDER BY combined_score DESC
        LIMIT :top_k
    """)
    
    # execute
    result = await db.execute(stmt, {
        "embedding": str(query_embedding),
        "query": query,
        "tenant_id": tenant_id,
        "threshold": similarity_threshold,
        "top_k": top_k
    })
    
    rows = result.fetchall()
    
    if not rows:
        return []
        
    chunk_ids = [r.chunk_id for r in rows]
    scores_map = {r.chunk_id: r.combined_score for r in rows}
    
    # fetch chunk entities
    chunks_stmt = select(KnowledgeChunk, KnowledgeDocument).join(KnowledgeDocument).where(KnowledgeChunk.id.in_(chunk_ids))
    chunks_result = await db.execute(chunks_stmt)
    chunks_with_docs = chunks_result.all()
    
    # construct contexts
    contexts = []
    for chunk, doc in chunks_with_docs:
        contexts.append(RetrievedContext(
            chunk=chunk,
            score=scores_map[chunk.id],
            doc=doc
        ))
        
    # sort back by score
    contexts.sort(key=lambda x: x.score, reverse=True)
    return contexts

def format_rag_context(contexts: List[RetrievedContext]) -> str:
    """Format retrieved contexts into XML-like string for LLM."""
    if not contexts:
        return "Relevant pricing or product information was not found in the provided knowledge base."
        
    parts = ["<historical_knowledge>"]
    for ctx in contexts:
        page_attr = f' page="{ctx.page_number}"' if ctx.page_number else ''
        parts.append(f'<source document="{ctx.filename}"{page_attr}>\n{ctx.content}\n</source>')
    parts.append("</historical_knowledge>")
    return "\n\n".join(parts)
