import json

from google import genai
from google.genai import types

from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_completion(prompt: str, system_prompt: str = "", model: str = None) -> str:
    model_name = model or settings.MODEL_NAME
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=2048,
    )
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config
    )
    return response.text

async def generate_structured(prompt: str, system_prompt: str = "", model: str = None) -> dict:
    sys_prompt = system_prompt + "\n\nPlease return ONLY valid JSON. No markdown formatting, no explanation."
    model_name = model or settings.MODEL_NAME
    config = types.GenerateContentConfig(
        system_instruction=sys_prompt,
        max_output_tokens=2048,
        response_mime_type="application/json"
    )
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config
    )
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())
