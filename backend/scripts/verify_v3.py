import sys
import os
import asyncio
import json

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.engine_v3 import init_v3_db
from src.mcp_tools.kvs_tools import write_layer, read_layer, list_layers

async def main():
    print("1. Initializing Semantic KVS Database...")
    await init_v3_db()
    print("Database initialized successfully.")

    print("\n2. Writing a 'customer:schema' layer...")
    schema_payload = json.dumps({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        }
    })
    result = await write_layer("customer:schema", "schema", schema_payload)
    print(f"Write Result: {result}")

    print("\n3. Writing a 'customer:data' layer...")
    data_payload = json.dumps([
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ])
    result = await write_layer("customer:data", "data", data_payload)
    print(f"Write Result: {result}")

    print("\n4. Listing all layers in the KVS...")
    layers = await list_layers()
    print(f"Layers: {layers}")

    print("\n5. Reading the 'customer:data' layer back...")
    layer_data = await read_layer("customer:data")
    print(f"Read Data: {layer_data}")

if __name__ == "__main__":
    asyncio.run(main())
