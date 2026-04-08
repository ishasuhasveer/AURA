from pymongo import MongoClient
from backend.config.settings import MONGO_URI

try:
    client = MongoClient(MONGO_URI)

    # This forces connection check
    client.admin.command('ping')

    print("✅ MongoDB Connected Successfully!")

except Exception as e:
    print("❌ Connection Failed")
    print(e)