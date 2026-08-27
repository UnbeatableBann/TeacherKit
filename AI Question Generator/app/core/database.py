from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_maker = None

    def init_db(self):
        if self.engine is None:
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                future=True,
                pool_size=5,
                max_overflow=10,
            )
            self.session_maker = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    async def init_schema(self):
        if self.engine is None:
            return
        
        # We need to explicitly import the models so that Base.metadata knows about them
        
        async with self.engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)

    async def close_db(self):
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None

db_manager = DatabaseManager()
Base = declarative_base()

async def get_db():
    if db_manager.session_maker is None:
        raise RuntimeError("Database not initialized. Call db_manager.init_db() first.")
    async with db_manager.session_maker() as session:
        yield session

