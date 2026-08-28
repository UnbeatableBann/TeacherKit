import json
import logging

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_structured[T: BaseModel](
    prompt: str,
    response_schema: type[T],
    system_prompt: str = "",
    model: str | None = None,
    max_retries: int | None = None,
) -> T:
    """
    Generate a structured response matching the Pydantic schema using Gemini.
    """
    model_name = model or settings.LLM_MODEL
    retries = (
        max_retries if max_retries is not None else settings.MAX_GENERATION_ATTEMPTS
    )

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=response_schema.model_json_schema(),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    last_err = None
    for attempt in range(retries):
        try:
            response = await client.aio.models.generate_content(
                model=model_name, contents=prompt, config=config
            )
            text = (response.text or "").strip()
            # Clean up markdown block if present
            text = text.removeprefix("```json")
            text = text.removesuffix("```")

            data = json.loads(text.strip())
            return response_schema(**data)
        except (ValueError, RuntimeError, json.JSONDecodeError, APIError) as e:
            logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
            last_err = e

    raise RuntimeError(
        f"Failed to generate structured output after {retries} attempts. Last error: {last_err}"
    )


import asyncio

import httpx


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Get vector embeddings using Gemini embedding model in batch with retries.
    Requests are chunked to avoid hitting API limits for large document batches.
    """
    model_name = settings.EMBEDDING_MODEL
    max_retries = settings.EMBEDDING_RETRY_COUNT
    chunk_size = settings.EMBEDDING_BATCH_SIZE

    all_embeddings: list[list[float]] = []

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:batchEmbedContents?key={settings.GEMINI_API_KEY}"

    async with httpx.AsyncClient() as http_client:
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i : i + chunk_size]
            last_err = None

            requests = []
            for text in chunk:
                requests.append(
                    {
                        "model": f"models/{model_name}",
                        "content": {"parts": [{"text": text}]},
                        "outputDimensionality": settings.EMBEDDING_DIMENSIONS,
                    }
                )

            for attempt in range(max_retries):
                try:
                    response = await http_client.post(url, json={"requests": requests})
                    response.raise_for_status()
                    data = response.json()

                    if "embeddings" not in data:
                        raise RuntimeError("No embeddings returned by API")

                    chunk_embeddings = [
                        emb.get("values", []) for emb in data["embeddings"]
                    ]

                    # Validate dimensions
                    for emb in chunk_embeddings:
                        if len(emb) != settings.EMBEDDING_DIMENSIONS:
                            raise ValueError(
                                f"EMBEDDING_DIMENSION_MISMATCH: expected {settings.EMBEDDING_DIMENSIONS}, got {len(emb)}"
                            )

                    all_embeddings.extend(chunk_embeddings)
                    break  # Success, proceed to next chunk

                except ValueError as e:
                    # Permanent failure if dimension mismatch
                    logger.error(str(e))
                    raise
                except (RuntimeError, httpx.HTTPError) as e:
                    logger.warning(
                        f"Embedding attempt {attempt + 1} failed for chunk {i}: {e}"
                    )
                    last_err = e
                    if attempt == max_retries - 1:
                        raise RuntimeError(
                            f"Failed to generate embeddings after {max_retries} attempts. Last error: {last_err}"
                        )
                    await asyncio.sleep(2**attempt)  # Exponential backoff

    return all_embeddings


async def get_embedding(text: str) -> list[float]:
    """
    Get vector embedding using Gemini embedding model.
    """
    res = await get_embeddings_batch([text])
    return res[0]
