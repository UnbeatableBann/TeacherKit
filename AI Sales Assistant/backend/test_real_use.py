import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.plugins.base import PluginContext, SessionState
from app.plugins.catalogue_retrieval import CatalogueRetrievalPlugin
from app.schemas.domain import RequirementSchema


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        from app.models.base import Base
        from app.models.domain import Product  # Ensure models are loaded
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        # 1. Insert test products directly
        p1 = Product(tenant_id="test", name="Cheap Phone", category="electronics", price=199, currency="USD", stock_status="in_stock", description="A cheap phone", specs={})
        p2 = Product(tenant_id="test", name="Expensive Phone", category="electronics", price=999, currency="USD", stock_status="in_stock", description="An expensive phone", specs={})
        p3 = Product(tenant_id="test", name="Tablet", category="electronics", price=499, currency="USD", stock_status="in_stock", description="A tablet", specs={})
        session.add_all([p1, p2, p3])
        await session.commit()
        
        plugin = CatalogueRetrievalPlugin()
        
        # Test 1: Category filter only
        state = SessionState(
            conversation_id="c1", 
            tenant_id="test", 
            requirements=RequirementSchema(category="electronics", features_wanted=[])
        )
        context = PluginContext(db=session, new_message="")
        
        print("\n--- Test 1: Category Filter ---")
        res = await plugin.run(state, context)
        products = res.get("retrieved_products", [])
        print(f"Retrieved {len(products)} products (expected 3)")
        assert len(products) == 3
        
        # Test 2: Category + Budget Max filter
        state.requirements.budget_max = 500
        print("\n--- Test 2: Category + Budget Max ---")
        res = await plugin.run(state, context)
        products = res.get("retrieved_products", [])
        print(f"Retrieved {len(products)} products (expected 2)")
        assert len(products) == 2
        
        # Test 3: Budget Min + Max filter
        state.requirements.budget_min = 200
        print("\n--- Test 3: Category + Budget Min + Max ---")
        res = await plugin.run(state, context)
        products = res.get("retrieved_products", [])
        print(f"Retrieved {len(products)} products (expected 1: Tablet)")
        assert len(products) == 1
        assert products[0]['name'] == 'Tablet'
        
        print("\nSUCCESS: Dynamic queries are working correctly!")

if __name__ == "__main__":
    asyncio.run(main())
