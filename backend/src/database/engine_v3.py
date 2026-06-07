import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.database.models_v3 import BaseV3

# Define the SQLite URL (KVS Store)
DB_PATH = os.getenv("DB_PATH", "sqlite+aiosqlite:///./microforce_v3.db")

# Create the Async Engine
# We use SQLite for the Semantic KVS because we only need rapid indexed string lookups
engine = create_async_engine(
    DB_PATH,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create an async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def init_v3_db():
    """
    Initializes the SQLite database with the Semantic KVS schema (EmpireLayer).
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseV3.metadata.create_all)

async def get_v3_session() -> AsyncSession: # type: ignore
    """
    Dependency to yield an async session.
    """
    async with AsyncSessionLocal() as session:
        yield session
