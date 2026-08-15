import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_database

router = APIRouter(prefix="/api/sandbox", tags=["Sandbox"])

class SandboxQueryRequest(BaseModel):
    prompt: str
    table_name: Optional[str] = "all"

def clean_sql(text: str) -> str:
    if not text:
        return ""
    return text.replace("```sql", "").replace("```", "").strip()

@router.post("/query")
async def execute_sandbox_query(req: SandboxQueryRequest):
    db = get_database()
    
    # Filter metadata by table if specified
    query_filter = {}
    if req.table_name and req.table_name != "all":
        query_filter["table_name"] = req.table_name

    tables = await db["tables_metadata"].find(query_filter, {"_id": 0}).to_list(length=100)
    
    if not tables:
        raise HTTPException(status_code=404, detail=f"No schema metadata found for target table '{req.table_name}'.")

    # Build targeted MCP context window
    scope_label = "ALL SCHEMAS" if req.table_name == "all" else f"TABLE: {req.table_name}"
    context_str = f"ACTIVE SCHEMA SCOPE: {scope_label}\nDATABASE SCHEMA & GOVERNANCE RULES:\n"
    
    dep_col_map = {}
    active_cols = []

    for tbl in tables:
        db_name = tbl.get('database', 'analytics_prod')
        t_name = tbl.get('table_name', 'table')
        context_str += f"\nTable: {db_name}.{t_name}\nDescription: {tbl.get('description', '')}\nColumns:\n"
        
        for col in tbl.get("columns", []):
            status = col.get("status")
            col_name = col.get("name")
            if status == "deprecated":
                rep = col.get("replacement_column", "active_column")
                dep_col_map[col_name.lower()] = rep
                context_str += f"  - [DEPRECATED COLUMN - DO NOT USE] '{col_name}' -> MUST REPLACE WITH: '{rep}'. Notice: {col.get('deprecation_notice', '')}\n"
            else:
                active_cols.append(col_name)
                context_str += f"  - [ACTIVE COLUMN] '{col_name}' ({col.get('data_type')})\n"

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model_name = "meta-llama/llama-3-8b-instruct:free"

    raw_sql = ""
    mcp_sql = ""
    detected_warnings = []

    # Detect prompt deprecated columns for fallback dynamic query generation
    found_deps = [dep for dep in dep_col_map if dep in req.prompt.lower()]

    if api_key and not api_key.startswith("sk-or-v1-your"):
        async with httpx.AsyncClient() as client:
            # 1. Raw Call (No Metadata Context)
            try:
                res_raw = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are a SQL generator. Return valid SQL query only without markdown block quotes."},
                            {"role": "user", "content": req.prompt}
                        ]
                    },
                    timeout=10.0
                )
                raw_sql = clean_sql(res_raw.json()['choices'][0]['message']['content'])
            except Exception:
                raw_sql = f"SELECT {', '.join(found_deps) if found_deps else '*'} FROM {tables[0]['table_name']};"

            # 2. ContextLens MCP-Enriched Call
            try:
                res_mcp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": f"You are a SQL generator.\n{context_str}\nRule: NEVER write SQL using deprecated columns. Replace deprecated columns with active replacements."},
                            {"role": "user", "content": req.prompt}
                        ]
                    },
                    timeout=10.0
                )
                mcp_sql = clean_sql(res_mcp.json()['choices'][0]['message']['content'])
            except Exception:
                mcp_cols = [dep_col_map[dep] for dep in found_deps] if found_deps else active_cols[:2]
                mcp_sql = f"SELECT {', '.join(mcp_cols)} FROM {tables[0]['table_name']};"
    else:
        # Dynamic Fallback Engine (No API key active)
        target_tbl = tables[0]['table_name']
        if found_deps:
            raw_cols = ", ".join(found_deps)
            mcp_cols = ", ".join([dep_col_map[dep] for dep in found_deps])
        else:
            if dep_col_map:
                first_dep = list(dep_col_map.keys())[0]
                raw_cols = first_dep
                mcp_cols = dep_col_map[first_dep]
            else:
                raw_cols = active_cols[0] if active_cols else "*"
                mcp_cols = raw_cols

        raw_sql = f"SELECT {raw_cols} FROM {target_tbl};"
        mcp_sql = f"SELECT {mcp_cols} FROM {target_tbl};"

    # Collect Governance Warnings for Deprecated Interceptions
    for tbl in tables:
        for col in tbl.get("columns", []):
            if col.get("status") == "deprecated":
                dep_col = col.get("name")
                rep_col = col.get("replacement_column")
                if dep_col.lower() in req.prompt.lower() or dep_col.lower() in raw_sql.lower():
                    detected_warnings.append(
                        f"Intercepted deprecated field '{dep_col}'. Rewrote query context to target active column '{rep_col}' on {tbl['table_name']}."
                    )

    return {
        "raw_sql": raw_sql,
        "mcp_sql": mcp_sql,
        "warnings": detected_warnings,
        "target_table": req.table_name,
        "mcp_prompt_context": context_str
    }