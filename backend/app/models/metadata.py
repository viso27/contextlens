from pydantic import BaseModel, Field
from typing import List, Optional

class ColumnSchema(BaseModel):
    name: str
    data_type: str
    description: str
    status: str = Field(default="active", description="'active' or 'deprecated'")
    replacement_column: Optional[str] = None
    deprecation_notice: Optional[str] = None
    is_pii: bool = False

class TableMetadata(BaseModel):
    database: str
    table_name: str
    description: str
    owner: str
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0)
    columns: List[ColumnSchema]