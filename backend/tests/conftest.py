import os
import pytest
import pytest_asyncio
import asyncio
import tempfile
import sys

# Ensure src can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Create temporary database and set environment variable immediately
# to prevent top-level imports in test modules from using the dev/prod database.
temp_db = tempfile.NamedTemporaryFile(delete=False)
temp_db.close()
os.environ["DB_PATH"] = f"sqlite+aiosqlite:///{temp_db.name}"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def setup_test_db():
    from src.database.engine import init_db, engine
    from src.database.queue_worker import queue_worker
    
    await init_db()
    
    # Start the worker
    worker_task = asyncio.create_task(queue_worker())
    
    yield
    
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    
    await engine.dispose()
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)
