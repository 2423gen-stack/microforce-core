import asyncio
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP

from src.database.engine import init_db, engine
from src.database.queue_worker import queue_worker, stop_queue_worker
from src.mcp.tools_data import mcp_insert_record, mcp_get_records
from src.mcp.tools_schema import apply_ai_schema

@asynccontextmanager
async def lifespan(server: FastMCP):
    """Lifespan context manager for FastMCP to initialize resources."""
    # Initialize DB tables
    await init_db()
    
    # Start the queue worker task
    worker_task = asyncio.create_task(queue_worker())
    
    yield
    
    # Teardown
    await stop_queue_worker()
    
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
        
    # Dispose SQLAlchemy engine
    await engine.dispose()

# Initialize FastMCP Server
mcp = FastMCP("Microforce", lifespan=lifespan)

@mcp.tool()
async def insert_record(class_name: str, payload_json: str) -> str:
    """
    Insert a new record into a specified model.
    class_name: The name of the Python class in models_ai.py (e.g., 'Customer')
    payload_json: A JSON string containing the data to insert.
    """
    return await mcp_insert_record(class_name, payload_json)

@mcp.tool()
async def get_records(class_name: str, filters_json: str = "{}") -> str:
    """
    Retrieve records from a specified model matching optional filters.
    class_name: The name of the Python class in models_ai.py.
    filters_json: A JSON string representing filter kwargs (e.g., '{"id": 1}').
    """
    return await mcp_get_records(class_name, filters_json)

@mcp.tool()
async def update_schema(new_python_code: str) -> str:
    """
    Overwrite the entire models_ai.py file to update the database schema dynamically.
    new_python_code: The full python source code for the new models_ai.py file.
    Must include 'from src.database.models_core import Base' and appropriate SQLAlchemy imports.
    """
    return await apply_ai_schema(new_python_code)

if __name__ == "__main__":
    # Start the FastMCP stdio server
    mcp.run()
