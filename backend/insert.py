from backend.database.collections_db import products_collection

products_collection.insert_one({
    "sku_name": "Test Cable",
    "specs": {
        "voltage_kv": 11,
        "conductor_material": "AL"
    }
})

print("✅ Product inserted!")