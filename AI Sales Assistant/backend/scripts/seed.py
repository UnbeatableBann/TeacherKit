import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base
from app.models.domain import Conversation, Customer, LeadScore


async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        # Seed test data
        cust1 = Customer(id="cust-1", tenant_id="default_tenant", name="Alice Smith", contact_info="alice@example.com")
        cust2 = Customer(id="cust-2", tenant_id="default_tenant", name="Bob Jones", contact_info="bob@example.com")
        session.add_all([cust1, cust2])
        await session.flush()
        
        conv1 = Conversation(id="conv-1", customer_id="cust-1", channel="web")
        conv2 = Conversation(id="conv-2", customer_id="cust-2", channel="web")
        session.add_all([conv1, conv2])
        await session.flush()
        
        ls1 = LeadScore(conversation_id="conv-1", score=85, breakdown={"budget_provided": 20, "high_urgency": 30, "features_identified": 10, "no_objections": 25})
        ls2 = LeadScore(conversation_id="conv-2", score=40, breakdown={"features_identified": 10, "budget_provided": 20, "no_objections": 10})
        session.add_all([ls1, ls2])
        
        await session.commit()
    
    print("Database seeded with sample leads!")

if __name__ == "__main__":
    asyncio.run(init_db())
