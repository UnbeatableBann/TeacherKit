from google import genai
from app.config import settings
import asyncio

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def get_embedding(text: str) -> list[float]:
    def _embed():
        return client.models.embed_content(
            model=settings.EMBEDDINGS_MODEL,
            contents=text
        )
    result = await asyncio.to_thread(_embed)
    return result.embeddings[0].values

async def get_embeddings(texts: list[str]) -> list[list[float]]:
    def _embed():
        return client.models.embed_content(
            model=settings.EMBEDDINGS_MODEL,
            contents=texts
        )
    result = await asyncio.to_thread(_embed)
    return [e.values for e in result.embeddings]
