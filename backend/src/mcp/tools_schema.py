import os
import importlib
from src.database.engine import engine, Base

from src.database.schema_validator import validate_schema_code

# We dynamically reload the models_ai module
import src.database.models_ai as models_ai

MODELS_AI_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "models_ai.py"
)

async def apply_ai_schema(new_content: str) -> str:
    """
    Overwrite models_ai.py with new_content, reload the module,
    and create new tables in the database.
    
    WARNING: This expects `new_content` to contain the full Python
    file content for `models_ai.py`, including imports.
    """
    try:
        # Validate the schema code before writing it
        is_valid, validation_msg = validate_schema_code(new_content, MODELS_AI_PATH)
        if not is_valid:
            return f"Validation failed: {validation_msg}"

        # Remove old tables from Base.metadata to prevent duplicate table errors on reload
        for attr_name in list(dir(models_ai)):
            attr = getattr(models_ai, attr_name)
            if isinstance(attr, type) and hasattr(attr, "__table__"):
                table = attr.__table__
                if table.key in Base.metadata.tables:
                    Base.metadata.remove(table)

        # Write the new schema
        with open(MODELS_AI_PATH, "w") as f:
            f.write(new_content)
            
        # Reload the module so Python is aware of the new classes
        importlib.reload(models_ai)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        return "Schema updated and tables created successfully."
    except Exception as e:
        return f"Error applying schema: {str(e)}"
