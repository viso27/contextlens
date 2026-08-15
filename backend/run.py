import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routes.metadata import router as metadata_router
from app.routes.evals_api import router as evals_api_router
from app.routes.sandbox import router as sandbox_router

load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Connect to MongoDB Atlas and auto-seed if empty
    await connect_to_mongo()
    db = get_database()
    if db is not None:
        count = await db["tables_metadata"].count_documents({})
        if count == 0:
            sample_table = {
                "database": "analytics_prod",
                "table_name": "user_transactions",
                "description": "Primary transactional database for all online order billing.",
                "trust_score": 0.95,
                "columns": [
                    {
                        "name": "transaction_id",
                        "data_type": "UUID",
                        "description": "Primary unique key for the transaction.",
                        "status": "active"
                    },
                    {
                        "name": "gross_amount",
                        "data_type": "DECIMAL(10,2)",
                        "description": "Raw charge amount before platform commissions.",
                        "status": "deprecated",
                        "replacement_column": "net_revenue",
                        "deprecation_notice": "DEPRECATED Q3 2026. Use 'net_revenue' to avoid billing mismatch."
                    },
                    {
                        "name": "net_revenue",
                        "data_type": "DECIMAL(10,2)",
                        "description": "Final realized revenue post-platform fees.",
                        "status": "active"
                    }
                ]
            }
            await db["tables_metadata"].insert_one(sample_table)
            print("🌱 Automatically seeded MongoDB Atlas with initial schema metadata.")
    
    yield
    
    # Shutdown logic: Close Mongo connection
    await close_mongo_connection()

app = FastAPI(
    title="ContextLens API Gateway",
    description="MCP Context Engine & Database Governance Evaluation Suite",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metadata_router)
app.include_router(evals_api_router)
app.include_router(sandbox_router)

@app.get("/")
async def root():
    return {"status": "online", "service": "ContextLens Core Engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)