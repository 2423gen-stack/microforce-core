import pytest
import asyncio
from src.mcp.tools_data import mcp_insert_record, mcp_get_records
from src.mcp.tools_schema import apply_ai_schema
import json

@pytest.mark.asyncio
async def test_concurrent_inserts():
    # First, read existing models_ai.py content to append ConcurrencyTestItem (Plan A compliant)
    import os
    from src.mcp.tools_schema import MODELS_AI_PATH
    
    existing_content = ""
    if os.path.exists(MODELS_AI_PATH):
        with open(MODELS_AI_PATH, "r") as f:
            existing_content = f.read()
            
    if "class ConcurrencyTestItem" not in existing_content:
        if not existing_content.strip():
            existing_content = "from sqlalchemy import Column, Integer, String\nfrom src.database.models_core import Base\n"
        schema_code = existing_content + """
class ConcurrencyTestItem(Base):
    __tablename__ = 'concurrency_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
"""
    else:
        schema_code = existing_content
        
    await apply_ai_schema(schema_code)
    
    # Perform 100 concurrent inserts
    tasks = []
    for i in range(100):
        payload = json.dumps({"name": f"item_{i}"})
        tasks.append(mcp_insert_record("ConcurrencyTestItem", payload))
        
    results = await asyncio.gather(*tasks)
    
    # Check that all were successful
    for res in results:
        data = json.loads(res)
        assert data["status"] == "success", f"Insertion failed: {data.get('message')}"
        
    # Check total count
    get_res = await mcp_get_records("ConcurrencyTestItem")
    get_data = json.loads(get_res)
    assert get_data["status"] == "success"
    assert len(get_data["data"]) == 100
