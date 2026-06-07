from sqlalchemy import String, JSON
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

BaseV3 = declarative_base()

class EmpireLayer(BaseV3):
    """
    Microforce-Coer (V3) Semantic KVS Core Table.
    Replaces traditional RDBMS tables with a unified 'Mille-feuille' layer architecture.
    """
    __tablename__ = 'empire_layers'
    
    # Unique identifier for the layer (e.g., 'customer:schema', 'customer:data')
    layer_key: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Type of layer (e.g., 'schema', 'data', 'ui_rules')
    layer_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    # The actual vectorized semantic content (can be schema definition or actual data arrays)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
