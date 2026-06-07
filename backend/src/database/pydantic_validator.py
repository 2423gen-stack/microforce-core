from typing import Any, Dict, Optional, Type
from pydantic import create_model, BaseModel

_pydantic_cache: Dict[Any, Type[BaseModel]] = {}

def get_pydantic_model(model_class) -> Type[BaseModel]:
    """
    Dynamically generates a Pydantic model based on a SQLAlchemy ORM class.
    """
    if model_class in _pydantic_cache:
        return _pydantic_cache[model_class]
        
    fields = {}
    for column in model_class.__table__.columns:
        python_type = Any
        if hasattr(column.type, "python_type"):
            try:
                python_type = column.type.python_type
            except NotImplementedError:
                pass
        
        # Determine if field is optional (nullable, has default, or primary key)
        is_optional = (
            column.nullable 
            or column.default is not None 
            or column.server_default is not None 
            or column.primary_key
        )
        
        if is_optional:
            fields[column.name] = (Optional[python_type], None)
        else:
            fields[column.name] = (python_type, ...)
            
    pydantic_model = create_model(f"{model_class.__name__}Schema", **fields)
    _pydantic_cache[model_class] = pydantic_model
    return pydantic_model
