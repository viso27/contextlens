from app.database import get_database

async def fetch_table_context(database: str, table_name: str) -> str:
    db = get_database()
    if db is None:
        return "Error: Database connection not active."

    record = await db["tables_metadata"].find_one({
        "database": database,
        "table_name": table_name
    })

    if not record:
        return f"Error: Schema metadata not found for {database}.{table_name}."

    lines = [
        f"=== Context Guardrail for Table: {record['database']}.{record['table_name']} ===",
        f"Description: {record['description']}",
        f"Owner: {record['owner']} | Trust Score: {record['trust_score']}",
        "\nColumn Definitions & Rules:"
    ]

    for col in record.get("columns", []):
        if col.get("status") == "deprecated":
            lines.append(
                f"⚠️ [DEPRECATED COLUMN] '{col['name']}': DO NOT USE. "
                f"Reason: {col.get('deprecation_notice', 'N/A')}. "
                f"Use replacement column: '{col.get('replacement_column')}' instead."
            )
        else:
            lines.append(f"✓ [ACTIVE COLUMN] '{col['name']}' ({col.get('data_type')}): {col.get('description')}")

    return "\n".join(lines)


async def check_query_safety(query: str, database: str, table_name: str) -> str:
    db = get_database()
    if db is None:
        return "Error: Database connection not active."

    record = await db["tables_metadata"].find_one({"database": database, "table_name": table_name})
    if not record:
        return "Validation skipped: No metadata registered."

    violations = []
    for col in record.get("columns", []):
        if col.get("status") == "deprecated" and col["name"] in query:
            violations.append(
                f"🚨 DEPRECATED COLUMN USAGE: '{col['name']}' is deprecated. Replace with '{col.get('replacement_column')}'."
            )

    if violations:
        return "VALIDATION FAILED:\n" + "\n".join(violations)
    return "SUCCESS: Query strictly respects active schema metadata."