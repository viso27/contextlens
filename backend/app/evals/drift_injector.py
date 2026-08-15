from app.database import get_database

async def inject_synthetic_drift(database: str, table_name: str, target_column: str, replacement_column: str):
    """Simulates database schema drift by programmatically marking a column as deprecated."""
    db = get_database()
    if db is None:
        return False

    result = await db["tables_metadata"].update_one(
        {"database": database, "table_name": table_name, "columns.name": target_column},
        {
            "$set": {
                "columns.$.status": "deprecated",
                "columns.$.replacement_column": replacement_column,
                "columns.$.deprecation_notice": f"Field '{target_column}' deprecated during synthetic drift test."
            }
        }
    )
    return result.modified_count > 0