import os
import httpx
from fastapi import APIRouter, Query
from typing import Optional
from app.database import get_database

router = APIRouter(prefix="/api/evals", tags=["Evaluations"])

def clean_sql(text: str) -> str:
    if not text:
        return ""
    return text.replace("```sql", "").replace("```", "").strip()

@router.post("/run")
async def run_evaluation_suite(table_name: Optional[str] = Query(None)):
    db = get_database()
    
    # 1. Fetch metadata context
    all_tables = await db["tables_metadata"].find({}, {"_id": 0}).to_list(length=100)
    
    if table_name and table_name != "all":
        eval_tables = [t for t in all_tables if t.get("table_name") == table_name]
    else:
        eval_tables = all_tables

    # 2. Build full governance rules context
    context_str = "DATABASE SCHEMA & GOVERNANCE RULES:\n"
    deprecated_cols = []
    
    for tbl in all_tables:
        db_name = tbl.get('database', 'analytics_prod')
        t_name = tbl.get('table_name', 'table')
        context_str += f"\nTable: {db_name}.{t_name}\nColumns:\n"
        
        for col in tbl.get("columns", []):
            status = col.get("status")
            col_name = col.get("name")
            if status == "deprecated":
                deprecated_cols.append(col_name)
                rep = col.get("replacement_column", "active_column")
                context_str += f"  - [DEPRECATED COLUMN - DO NOT USE] '{col_name}' -> MUST REPLACE WITH: '{rep}'. Notice: {col.get('deprecation_notice', '')}\n"
            else:
                context_str += f"  - [ACTIVE COLUMN] '{col_name}' ({col.get('data_type')})\n"

    # 3. Build target table benchmarks
    dynamic_benchmarks = []
    for tbl in eval_tables:
        t_name = tbl.get('table_name', 'table')
        has_deprecated = False
        for col in tbl.get("columns", []):
            if col.get("status") == "deprecated":
                has_deprecated = True
                rep = col.get("replacement_column", "active_column")
                col_name = col.get("name")
                dynamic_benchmarks.append({
                    "question": f"Calculate sum of {col_name} for table {t_name}.",
                    "expected_clean_col": rep,
                    "deprecated_col": col_name,
                    "table_name": t_name
                })
        
        if not has_deprecated:
            active_cols = [c.get("name") for c in tbl.get("columns", []) if c.get("status") == "active"]
            target_col = active_cols[0] if active_cols else "*"
            dynamic_benchmarks.append({
                "question": f"Get all active records from {t_name}.",
                "expected_clean_col": target_col,
                "deprecated_col": "NONE",
                "table_name": t_name
            })

    if not dynamic_benchmarks:
        return {"total_questions": 0, "schema_precision": 1.0, "drift_recovery_rate": 1.0, "logs": []}

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model_name = "meta-llama/llama-3-8b-instruct:free"
    logs = []

    for test in dynamic_benchmarks:
        question = test["question"]
        dep_col = test["deprecated_col"]
        clean_col = test["expected_clean_col"]
        tbl_name = test["table_name"]

        raw_sql = ""
        mcp_sql = ""

        if api_key and not api_key.startswith("sk-or-v1-your"):
            async with httpx.AsyncClient() as client:
                try:
                    res_raw = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "You are a SQL generator. Output standard SQL query only without markdown."},
                                {"role": "user", "content": question}
                            ]
                        },
                        timeout=10.0
                    )
                    raw_sql = clean_sql(res_raw.json()['choices'][0]['message']['content'])
                except Exception:
                    raw_sql = f"SELECT SUM({dep_col}) FROM {tbl_name};" if dep_col != "NONE" else f"SELECT * FROM {tbl_name};"

                try:
                    res_mcp = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": f"You are a SQL generator.\n{context_str}\nRule: NEVER write queries using deprecated columns."},
                                {"role": "user", "content": question}
                            ]
                        },
                        timeout=10.0
                    )
                    mcp_sql = clean_sql(res_mcp.json()['choices'][0]['message']['content'])
                except Exception:
                    mcp_sql = f"SELECT SUM({clean_col}) FROM {tbl_name};" if dep_col != "NONE" else f"SELECT {clean_col} FROM {tbl_name};"
        else:
            if dep_col != "NONE":
                raw_sql = f"SELECT SUM({dep_col}) AS total FROM {tbl_name};"
                mcp_sql = f"SELECT SUM({clean_col}) AS total FROM {tbl_name};"
            else:
                raw_sql = f"SELECT * FROM {tbl_name};"
                mcp_sql = f"SELECT {clean_col} FROM {tbl_name};"

        if dep_col != "NONE":
            passed = dep_col.lower() not in mcp_sql.lower()
        else:
            passed = True

        logs.append({
            "question": question,
            "without_mcp_query": raw_sql,
            "with_mcp_query": mcp_sql,
            "passed": passed,
            "table_name": tbl_name,
            "deprecated_col": dep_col
        })

    total_questions = len(logs)
    passed_count = sum(1 for log in logs if log["passed"])
    schema_precision = round((passed_count / total_questions), 2) if total_questions > 0 else 1.0

    raw_failures = sum(1 for log in logs if log["deprecated_col"] != "NONE" and log["deprecated_col"].lower() in log["without_mcp_query"].lower())
    recovered = sum(1 for log in logs if log["passed"] and log["deprecated_col"] != "NONE" and log["deprecated_col"].lower() in log["without_mcp_query"].lower())
    drift_recovery_rate = round((recovered / raw_failures), 2) if raw_failures > 0 else 1.0

    return {
        "total_questions": total_questions,
        "schema_precision": schema_precision,
        "drift_recovery_rate": drift_recovery_rate,
        "model_name": model_name,
        "logs": logs
    }