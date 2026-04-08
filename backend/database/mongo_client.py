from pymongo import MongoClient
from backend.config.settings import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)

# Verify connection
client.admin.command("ping")

db = client[DB_NAME]


# -------- PRODUCT QUERIES --------

def get_all_products():
    """
    Fetch all SKUs from MongoDB.
    Returns list of dicts.
    """
    return list(db["products"].find({}, {"_id": 0}))


def get_product_by_sku(sku_id: str):
    """
    Fetch a single SKU.
    """
    return db["products"].find_one({"sku_id": sku_id}, {"_id": 0})

print("Connected DB:", DB_NAME)
print("Mongo URI:", MONGO_URI)