from typing import List

def calculate_schema_precision(queries: List[str], deprecated_columns: List[str]) -> float:
    """Calculates the percentage of LLM responses that successfully avoided deprecated schema fields."""
    if not queries:
        return 1.0
    
    clean_queries = sum(1 for q in queries if not any(col in q for col in deprecated_columns))
    return round(clean_queries / len(queries), 2)

def calculate_drift_recovery_rate(passed_count: int, total_count: int) -> float:
    if total_count == 0:
        return 0.0
    return round(passed_count / total_count, 2)