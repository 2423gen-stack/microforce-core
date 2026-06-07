import pytest
import json
from src.mcp.tools_schema import apply_ai_schema
from src.mcp.tools_data import mcp_insert_record, mcp_get_records

@pytest.mark.asyncio
async def test_dynamic_schema_application():
    # Read existing models_ai.py content to append Product (Plan A compliant)
    import os
    from src.mcp.tools_schema import MODELS_AI_PATH
    
    existing_content = ""
    if os.path.exists(MODELS_AI_PATH):
        with open(MODELS_AI_PATH, "r") as f:
            existing_content = f.read()
            
    if "class Product" not in existing_content:
        if not existing_content.strip():
            existing_content = "from sqlalchemy import Column, Integer, String\nfrom src.database.models_core import Base\n"
        schema_code = existing_content + """
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
"""
    else:
        schema_code = existing_content

    # Apply new schema
    res = await apply_ai_schema(schema_code)
    assert "successfully" in res or "Schema updated" in res
    
    # Insert record using the new schema
    payload = json.dumps({"title": "Test Product", "price": 999})
    insert_res = await mcp_insert_record("Product", payload)
    
    data = json.loads(insert_res)
    assert data["status"] == "success"
    assert data["data"]["title"] == "Test Product"
    
    # Retrieve record
    get_res = await mcp_get_records("Product", json.dumps({"id": data["data"]["id"]}))
    get_data = json.loads(get_res)
    assert get_data["status"] == "success"
    assert len(get_data["data"]) == 1
    assert get_data["data"][0]["title"] == "Test Product"
    assert get_data["data"][0]["price"] == 999
