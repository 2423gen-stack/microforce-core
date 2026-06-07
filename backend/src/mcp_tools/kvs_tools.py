import json
from sqlalchemy.future import select
from mcp.server.fastmcp import FastMCP
from src.database.models_v3 import EmpireLayer
from src.database.engine_v3 import AsyncSessionLocal, init_v3_db

# Create the V3 MCP Server Instance
# This exposes the Semantic KVS engine directly to external AI agents
mcp_v3 = FastMCP("microforce-coer-v3")

@mcp_v3.tool()
async def read_layer(layer_key: str) -> str:
    """
    Read a semantic layer from the Microforce KVS engine by its key.
    This bypasses traditional SQL joins, fetching the entire layer payload directly.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(EmpireLayer).where(EmpireLayer.layer_key == layer_key))
        layer = result.scalar_one_or_none()
        if layer:
            return json.dumps({
                "layer_key": layer.layer_key,
                "layer_type": layer.layer_type,
                "payload": layer.payload
            }, ensure_ascii=False, indent=2)
        return f"Layer '{layer_key}' not found."

@mcp_v3.tool()
async def write_layer(layer_key: str, layer_type: str, payload_json: str) -> str:
    """
    Write or update a semantic layer in the Microforce KVS engine.
    The payload must be a valid JSON string representing the layer's multi-dimensional data.
    """
    try:
        payload_dict = json.loads(payload_json)
    except json.JSONDecodeError as e:
        return f"Failed to parse payload_json: {e}"

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if layer exists
            result = await session.execute(select(EmpireLayer).where(EmpireLayer.layer_key == layer_key))
            layer = result.scalar_one_or_none()
            
            if layer:
                layer.layer_type = layer_type
                layer.payload = payload_dict
                action = "updated"
            else:
                layer = EmpireLayer(
                    layer_key=layer_key,
                    layer_type=layer_type,
                    payload=payload_dict
                )
                session.add(layer)
                action = "created"
        
        return f"Successfully {action} layer '{layer_key}' of type '{layer_type}'."

@mcp_v3.tool()
async def list_layers() -> str:
    """
    List all available semantic layers in the KVS engine.
    Returns a list of layer keys and their types.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(EmpireLayer.layer_key, EmpireLayer.layer_type))
        layers = [{"key": r[0], "type": r[1]} for r in result.all()]
        return json.dumps(layers, indent=2)
