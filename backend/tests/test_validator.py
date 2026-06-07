import tempfile
import os
import pytest
from src.database.schema_validator import validate_schema_code

def test_valid_schema():
    code = """
from sqlalchemy import Column, Integer, String
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
    
    try:
        ok, msg = validate_schema_code(code, path)
        assert ok, msg
    finally:
        os.unlink(path)

def test_invalid_import():
    code = """
import os
from sqlalchemy import Column, Integer
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
        
    try:
        ok, msg = validate_schema_code(code, path)
        assert not ok
        assert "Security Error" in msg
    finally:
        os.unlink(path)

def test_module_level_expression():
    code = """
from sqlalchemy import Column, Integer
from src.database.models_core import Base

print("Malicious Execution")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
        
    try:
        ok, msg = validate_schema_code(code, path)
        assert not ok
        assert "Security Error" in msg
    finally:
        os.unlink(path)

def test_plan_a_violation_delete():
    old_code = """
from sqlalchemy import Column, Integer
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
"""
    new_code = """
from sqlalchemy import Column, Integer
from src.database.models_core import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(old_code)
        path = f.name
        
    try:
        ok, msg = validate_schema_code(new_code, path)
        assert not ok
        assert "Plan A Violation" in msg
        assert "cannot be deleted" in msg
    finally:
        os.unlink(path)

def test_plan_a_violation_modify():
    old_code = """
from sqlalchemy import Column, Integer
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
"""
    # User class modified (adding name column or changing layout)
    new_code = """
from sqlalchemy import Column, Integer, String
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(old_code)
        path = f.name
        
    try:
        ok, msg = validate_schema_code(new_code, path)
        assert not ok
        assert "Plan A Violation" in msg
        assert "cannot be modified" in msg
    finally:
        os.unlink(path)

def test_plan_a_success_append():
    old_code = """
from sqlalchemy import Column, Integer
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
"""
    new_code = """
from sqlalchemy import Column, Integer, String
from src.database.models_core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(old_code)
        path = f.name
        
    try:
        ok, msg = validate_schema_code(new_code, path)
        assert ok, msg
    finally:
        os.unlink(path)
