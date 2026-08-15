from fastapi import APIRouter, HTTPException
from app.database import get_database
from typing import List, Dict, Any

router = APIRouter(prefix="/api/metadata", tags=["Metadata"])

@router.get("/")
async def get_all_metadata():
    db = get_database()
    cursor = db["tables_metadata"].find({}, {"_id": 0})
    return await cursor.to_list(length=100)

@router.post("/")
async def add_table_metadata(table_data: Dict[str, Any]):
    db = get_database()
    if not table_data.get("table_name"):
        raise HTTPException(status_code=400, detail="table_name is required")
    
    table_data.setdefault("trust_score", 0.95)
    table_data.setdefault("database", "analytics_prod")
    table_data.setdefault("columns", [])
    table_data.setdefault("sample_data", [])
    
    # Save schema definition and sample rows dynamically to MongoDB Atlas
    await db["tables_metadata"].update_one(
        {"table_name": table_data["table_name"]},
        {"$set": table_data},
        upsert=True
    )
    return {"status": "success", "message": f"Schema for {table_data['table_name']} successfully created."}

@router.delete("/{table_name}")
async def delete_table_metadata(table_name: str):
    db = get_database()
    res = await db["tables_metadata"].delete_one({"table_name": table_name})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"status": "success", "message": f"Table {table_name} deleted."}