from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models.metadata import TableMetadata

router = APIRouter(prefix="/api/metadata", tags=["Metadata"])

@router.get("/")
async def get_all_metadata():
    db = get_database()
    if db is None:
        return []
    cursor = db["tables_metadata"].find({}, {"_id": 0})
    return await cursor.to_list(length=100)

@router.post("/")
async def create_or_update_metadata(table_data: TableMetadata):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection uninitialized")
    
    await db["tables_metadata"].update_one(
        {"database": table_data.database, "table_name": table_data.table_name},
        {"$set": table_data.model_dump()},
        upsert=True
    )
    return {"message": "Schema metadata saved successfully!"}