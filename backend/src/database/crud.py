from sqlalchemy import select
from src.database.engine import AsyncSessionLocal
from src.database.queue_worker import enqueue_write_operation
import src.database.models_ai as models_ai

async def _insert_record_task(model_class, payload: dict):
    """Actual database insertion logic, runs inside the worker."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            instance = model_class(**payload)
            session.add(instance)
            await session.flush()
            # Return a dict representation to avoid detached instance issues
            return {c.name: getattr(instance, c.name) for c in model_class.__table__.columns}

from src.database.pydantic_validator import get_pydantic_model

async def insert_record(class_name: str, payload: dict):
    """
    Public API to insert a record safely via the queue.
    """
    # Find the model class dynamically
    model_class = getattr(models_ai, class_name, None)
    if not model_class:
        raise ValueError(f"Model class '{class_name}' not found in models_ai.")
    
    # Validate payload using dynamic Pydantic model
    pydantic_model = get_pydantic_model(model_class)
    validated_obj = pydantic_model.model_validate(payload)
    # Convert back to dict, excluding fields that were not set (e.g. autoincrement primary keys)
    validated_payload = validated_obj.model_dump(exclude_unset=True)
    
    # Enqueue the write operation to prevent locks
    return await enqueue_write_operation(_insert_record_task, model_class, validated_payload)

async def get_records(class_name: str, **filters):
    """
    Read operations do not need the queue.
    SQLite handles concurrent reads well.
    """
    model_class = getattr(models_ai, class_name, None)
    if not model_class:
        raise ValueError(f"Model class '{class_name}' not found in models_ai.")

    async with AsyncSessionLocal() as session:
        stmt = select(model_class)
        for key, value in filters.items():
            if hasattr(model_class, key):
                stmt = stmt.where(getattr(model_class, key) == value)
        
        result = await session.execute(stmt)
        records = result.scalars().all()
        return [{c.name: getattr(r, c.name) for c in model_class.__table__.columns} for r in records]
