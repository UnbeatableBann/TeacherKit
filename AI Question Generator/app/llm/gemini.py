import json
import logging

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_structured[T](
    prompt: str,
    response_schema: type[T],
    system_prompt: str = "",
    model: str | None = None,
    max_retries: int = 3,
) -> T:
    """
    Generate a structured response matching the Pydantic schema using Gemini.
    """
    model_name = model or settings.LLM_MODEL

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=response_schema.model_json_schema(),  # type: ignore
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    last_err = None
    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model=model_name, contents=prompt, config=config
            )
            text = response.text.strip()  # type: ignore
            # Clean up markdown block if present
            text = text.removeprefix("```json")
            text = text.removesuffix("```")

            data = json.loads(text.strip())
            return response_schema(**data)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
            last_err = e

    raise RuntimeError(
        f"Failed to generate structured output after {max_retries} attempts. Last error: {last_err}"
    )


import asyncio


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Get vector embeddings using Gemini embedding model in batch with retries.
    Requests are chunked to avoid hitting API limits for large document batches.
    """
    model_name = settings.EMBEDDING_MODEL
    max_retries = 3
    chunk_size = 100
    
    all_embeddings: list[list[float]] = []
    
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        last_err = None
        
        for attempt in range(max_retries):
            try:
                response = await client.aio.models.embed_content(
                    model=model_name, contents=chunk
                )
                if not response.embeddings:
                    raise RuntimeError("No embeddings returned by API")
                
                chunk_embeddings = [emb.values for emb in response.embeddings]  # type: ignore
                
                # Validate dimensions
                for emb in chunk_embeddings:
                    if len(emb) != settings.EMBEDDING_DIMENSIONS:  # type: ignore
                        raise ValueError(f"EMBEDDING_DIMENSION_MISMATCH: expected {settings.EMBEDDING_DIMENSIONS}, got {len(emb)}")  # type: ignore
                
                all_embeddings.extend(chunk_embeddings)  # type: ignore
                break  # Success, proceed to next chunk
                
            except ValueError as e:
                # Permanent failure if dimension mismatch
                logger.error(str(e))
                raise
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Embedding attempt {attempt + 1} failed for chunk {i}: {e}")
                last_err = e
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"Failed to generate embeddings after {max_retries} attempts. Last error: {last_err}"
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    return all_embeddings

async def get_embedding(text: str) -> list[float]:
    """
    Get vector embedding using Gemini embedding model.
    """
    res = await get_embeddings_batch([text])
    return res[0]
