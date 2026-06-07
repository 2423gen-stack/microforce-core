import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.database.models_core import Base
# Import models_ai so that Base.metadata knows about them
import src.database.models_ai

# Use a local SQLite file for the prototype
DB_PATH = os.getenv("DB_PATH", "sqlite+aiosqlite:///microforce.db")

# Create the async engine
engine = create_async_engine(
    DB_PATH,
    echo=False,
    # SQLite requires check_same_thread=False for async/queue workers
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

async def init_db():
    """Create all tables defined in Base.metadata"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
