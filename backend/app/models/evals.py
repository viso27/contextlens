from pydantic import BaseModel
from typing import List

class EvalQuestion(BaseModel):
    id: str
    question: str
    expected_active_columns: List[str]
    target_table: str
    target_db: str

class EvalRunLog(BaseModel):
    question: str
    without_mcp_query: str
    with_mcp_query: str
    drift_detected: bool
    passed: bool

class EvalRunResult(BaseModel):
    scenario_name: str
    timestamp: str
    model_name: str
    total_questions: int
    schema_precision: float
    drift_recovery_rate: float
    logs: List[EvalRunLog]