import pytest
from pydantic import ValidationError
from sqlalchemy import Column, Integer, String
from src.database.models_core import Base
from src.database.pydantic_validator import get_pydantic_model
from src.database.crud import insert_record, get_records
from src.database.engine import engine

class ValidationDummyModel(Base):
    __tablename__ = 'test_validation_table'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)

@pytest.mark.asyncio
async def test_pydantic_model_generation():
    pyd_model = get_pydantic_model(ValidationDummyModel)
    
    # Valid data
    valid_data = {"name": "Alice", "age": 25}
    obj = pyd_model.model_validate(valid_data)
    assert obj.name == "Alice"
    assert obj.age == 25
    assert obj.id is None  # Optional
    
    # Missing required field (name)
    with pytest.raises(ValidationError):
        pyd_model.model_validate({"age": 30})
        
    # Invalid type
    with pytest.raises(ValidationError):
        pyd_model.model_validate({"name": "Bob", "age": "not-a-number"})

@pytest.mark.asyncio
async def test_insert_validation_success(setup_test_db):
    # Register the ValidationDummyModel class inside models_ai dynamically for testing
    import src.database.models_ai as models_ai
    setattr(models_ai, "ValidationDummyModel", ValidationDummyModel)
    
    # Create the table
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    try:
        # Should succeed
        result = await insert_record("ValidationDummyModel", {"name": "Charlie_success", "age": 40})
        assert result["name"] == "Charlie_success"
        assert result["age"] == 40
        assert result["id"] is not None
        
        # Check database
        records = await get_records("ValidationDummyModel", name="Charlie_success")
        assert len(records) == 1
        assert records[0]["age"] == 40
    finally:
        delattr(models_ai, "ValidationDummyModel")

@pytest.mark.asyncio
async def test_insert_validation_failure(setup_test_db):
    import src.database.models_ai as models_ai
    setattr(models_ai, "ValidationDummyModel", ValidationDummyModel)
    
    # Create the table
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    try:
        # Invalid data type (age is string instead of integer)
        with pytest.raises(ValidationError):
            await insert_record("ValidationDummyModel", {"name": "Charlie", "age": "invalid-age"})
            
        # Missing required field 'name'
        with pytest.raises(ValidationError):
            await insert_record("ValidationDummyModel", {"age": 50})
    finally:
        delattr(models_ai, "ValidationDummyModel")
