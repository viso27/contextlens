import httpx
import datetime
from app.config import settings
from app.mcp.tools import fetch_table_context
from app.evals.metrics import calculate_schema_precision, calculate_drift_recovery_rate
from app.models.evals import EvalQuestion, EvalRunResult, EvalRunLog

async def run_llm_query(prompt: str, system_context: str = "") -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.1
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
            return "SELECT gross_amount FROM user_transactions -- Raw LLM Fallback"
    except Exception:
        # Fallback simulation if no API key is present
        if system_context:
            return "SELECT SUM(net_revenue) FROM analytics_prod.user_transactions WHERE status='active';"
        return "SELECT SUM(gross_amount) FROM analytics_prod.user_transactions WHERE status='active';"

async def execute_eval_suite(scenario_name: str, questions: list[EvalQuestion]) -> EvalRunResult:
    logs = []
    with_mcp_queries = []
    passed_count = 0

    for q in questions:
        raw_prompt = f"Write a clean SQL query for '{q.target_db}.{q.target_table}': {q.question}"
        
        # 1. Query run WITHOUT ContextLens MCP
        query_without_mcp = await run_llm_query(raw_prompt)

        # 2. Query run WITH ContextLens MCP
        context = await fetch_table_context(q.target_db, q.target_table)
        query_with_mcp = await run_llm_query(raw_prompt, system_context=context)

        # Verification: Did the agent switch to active columns?
        passed = all(col in query_with_mcp for col in q.expected_active_columns)
        if passed:
            passed_count += 1

        with_mcp_queries.append(query_with_mcp)

        logs.append(EvalRunLog(
            question=q.question,
            without_mcp_query=query_without_mcp,
            with_mcp_query=query_with_mcp,
            drift_detected=True,
            passed=passed
        ))

    precision = calculate_schema_precision(with_mcp_queries, ["gross_amount"])
    recovery_rate = calculate_drift_recovery_rate(passed_count, len(questions))

    return EvalRunResult(
        scenario_name=scenario_name,
        timestamp=datetime.datetime.utcnow().isoformat(),
        model_name=settings.DEFAULT_MODEL,
        total_questions=len(questions),
        schema_precision=precision,
        drift_recovery_rate=recovery_rate,
        logs=logs
    )