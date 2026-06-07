
from sqlalchemy import Column, Integer, String
from src.database.models_core import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

class ConcurrencyTestItem(Base):
    __tablename__ = 'concurrency_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
