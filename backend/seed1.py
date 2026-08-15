import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import connect_to_mongo, get_database, close_mongo_connection

# 1. Fintech / Billing Domain
FINTECH_SCHEMA = {
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
        },
        {
            "name": "payment_gateway",
            "data_type": "VARCHAR(50)",
            "description": "Processor used for transaction settlement (e.g. Stripe, Razorpay).",
            "status": "active",
            "is_pii": False
        }
    ]
}

# 2. SaaS Customer Billing Domain
SAAS_BILLING_SCHEMA = {
    "database": "billing_db",
    "table_name": "customer_subscriptions",
    "description": "Tracks SaaS customer tier subscriptions and annual recurring rates.",
    "owner": "Growth Engineering",
    "trust_score": 0.91,
    "columns": [
        {
            "name": "subscription_id",
            "data_type": "UUID",
            "description": "Unique identifier for subscription instance.",
            "status": "active",
            "is_pii": False
        },
        {
            "name": "legacy_plan_rate",
            "data_type": "DECIMAL(10,2)",
            "description": "Legacy unadjusted subscription rate.",
            "status": "deprecated",
            "replacement_column": "arr_usd",
            "deprecation_notice": "Unconverted for multi-currency accounts. Use 'arr_usd'.",
            "is_pii": False
        },
        {
            "name": "arr_usd",
            "data_type": "DECIMAL(10,2)",
            "description": "Standardized Annual Recurring Revenue normalized in USD.",
            "status": "active",
            "is_pii": False
        },
        {
            "name": "user_phone",
            "data_type": "VARCHAR(20)",
            "description": "Unformatted raw customer phone number.",
            "status": "deprecated",
            "replacement_column": "contact_phone_e164",
            "deprecation_notice": "Violates phone storage standards. Use E.164 formatted 'contact_phone_e164'.",
            "is_pii": True
        },
        {
            "name": "contact_phone_e164",
            "data_type": "VARCHAR(20)",
            "description": "Compliant E.164 standard formatted phone string.",
            "status": "active",
            "is_pii": True
        }
    ]
}

# 3. Product Analytics / Telemetry Domain
PRODUCT_ANALYTICS_SCHEMA = {
    "database": "telemetry_events",
    "table_name": "user_activity_logs",
    "description": "Clickstream and event telemetry logs captured across clients.",
    "owner": "Data Platform Team",
    "trust_score": 0.88,
    "columns": [
        {
            "name": "event_id",
            "data_type": "UUID",
            "description": "Unique log entry identifier.",
            "status": "active",
            "is_pii": False
        },
        {
            "name": "user_ip_address",
            "data_type": "VARCHAR(45)",
            "description": "Raw IPv4 or IPv6 client internet protocol address.",
            "status": "deprecated",
            "replacement_column": "anonymized_ip_hash",
            "deprecation_notice": "DEPRECATED for GDPR/CCPA compliance. Use 'anonymized_ip_hash'.",
            "is_pii": True
        },
        {
            "name": "anonymized_ip_hash",
            "data_type": "VARCHAR(64)",
            "description": "SHA-256 salted hash of client IP address.",
            "status": "active",
            "is_pii": False
        },
        {
            "name": "session_duration_sec",
            "data_type": "INTEGER",
            "description": "Active web or mobile session duration measured in seconds.",
            "status": "active",
            "is_pii": False
        }
    ]
}

async def seed_data():
    await connect_to_mongo()
    db = get_database()
    
    if db is None:
        print("❌ DB connection failed. Check your MONGO_URI in .env")
        return

    # Clear existing metadata to prevent duplicates
    await db["tables_metadata"].delete_many({})

    # Insert 3 sample schemas
    seeds = [FINTECH_SCHEMA, SAAS_BILLING_SCHEMA, PRODUCT_ANALYTICS_SCHEMA]
    await db["tables_metadata"].insert_many(seeds)
    
    print(f"🌱 Successfully seeded MongoDB Atlas with {len(seeds)} schemas!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_data())