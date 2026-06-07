import json
from src.database.crud import insert_record, get_records

async def mcp_insert_record(class_name: str, payload_json: str) -> str:
    """
    Insert a record into the database.
    payload_json should be a JSON string representing the dictionary of values.
    """
    try:
        payload = json.loads(payload_json)
        result = await insert_record(class_name, payload)
        return json.dumps({"status": "success", "data": result})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

async def mcp_get_records(class_name: str, filters_json: str = "{}") -> str:
    """
    Retrieve records from the database.
    filters_json should be a JSON string representing filter kwargs.
    """
    try:
        filters = json.loads(filters_json)
        records = await get_records(class_name, **filters)
        return json.dumps({"status": "success", "data": records})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
