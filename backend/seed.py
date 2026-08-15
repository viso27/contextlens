import asyncio
from app.database import connect_to_mongo, get_database, close_mongo_connection

async def seed_data():
    await connect_to_mongo()
    db = get_database()
    
    if db is None:
        print("❌ DB connection failed. Check your MONGO_URI in .env")
        return

    # Clear existing metadata to prevent duplicates
    await db["tables_metadata"].delete_many({})

    # Insert sample table with active and deprecated columns
    sample_table = {
        "database": "analytics_prod",
        "table_name": "user_transactions",
        "description": "Primary transactional database for all online order billing.",
        "owner": "Finance Tech Team",
        "trust_score": 0.95,
        "columns": [
            {
                "name": "transaction_id",
                "data_type": "UUID",
                "description": "Primary unique key for the transaction.",
                "status": "active",
                "is_pii": False
            },
            {
                "name": "gross_amount",
                "data_type": "DECIMAL(10,2)",
                "description": "Raw charge amount before platform commissions.",
                "status": "deprecated",
                "replacement_column": "net_revenue",
                "deprecation_notice": "DEPRECATED Q3 2026. Use 'net_revenue' to avoid billing mismatch.",
                "is_pii": False
            },
            {
                "name": "net_revenue",
                "data_type": "DECIMAL(10,2)",
                "description": "Final realized revenue post-platform fees.",
                "status": "active",
                "is_pii": False
            }
        ]
    }

    await db["tables_metadata"].insert_one(sample_table)
    print("🌱 Seeded MongoDB Atlas with sample schema metadata!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_data())