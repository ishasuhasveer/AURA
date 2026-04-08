from backend.database.mongo_client import db

products_collection = db["products"]
pricing_collection = db["pricing"]
rfps_collection = db["rfps"]
rfp_decisions_collection = db["rfp_decisions"]
companies_collection = db["companies"]