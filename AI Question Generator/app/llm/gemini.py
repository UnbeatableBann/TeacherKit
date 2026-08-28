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
        response_schema=response_schema.model_json_schema(),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    last_err = None
    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model=model_name, contents=prompt, config=config
            )
            text = response.text.strip()
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


async def get_embedding(text: str) -> list[float]:
    """
    Get vector embedding using Gemini embedding model.
    """
    response = await client.aio.models.embed_content(
        model="gemini-embedding-2", contents=text
    )
    return response.embeddings[0].values
