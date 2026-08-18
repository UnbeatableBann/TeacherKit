from sqlalchemy import select

from app.llm_client import generate_completion
from app.models.domain import Product, Recommendation
from app.plugins.base import PluginBase, PluginContext, SessionState


class FollowUpGeneratorPlugin(PluginBase):
    async def run(self, state: SessionState, context: PluginContext) -> str:
        # Get validated recommendations shown so far
        result = await context.db.execute(
            select(Recommendation, Product)
            .join(Product, Recommendation.product_id == Product.id)
            .where(Recommendation.conversation_id == state.conversation_id)
        )
        recs_data = result.all()
        
        recs_text = ""
        for rec, prod in recs_data:
            recs_text += f"- {prod.name}: ${prod.price} ({rec.reasoning})\n"
            
        prompt = f"""
Customer Requirements:
{state.requirements.model_dump_json()}

Recommendations Presented:
{recs_text}

Conversation Summary:
{state.summary}

Write a professional follow-up email to the customer summarizing their needs and our recommendations. Do NOT invent new prices or products.
"""
        system_prompt = "You are a professional sales agent drafting a follow-up email. Only use confirmed data."
        draft = await generate_completion(prompt, system_prompt)
        return draft
