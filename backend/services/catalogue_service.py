from backend.catalogue.extractor import CatalogueExtractor
from backend.catalogue.parser import CatalogueParser
from backend.database.collections_db import products_collection


def process_catalogue(file_path: str):

    extractor = CatalogueExtractor()
    parser = CatalogueParser()

    print("📄 Extracting catalogue...")
    extracted = extractor.extract(file_path)

    print("🧠 Parsing catalogue...")
    products = parser.parse(extracted)

    print(f"✅ Clean products: {len(products)}")

    db_products = []

    for p in products:

        size = int(p["size_mm2"])

        db_product = {
            "sku_id": f"CABLE_{size}",
            "sku_name": f"XLPE Cable {size} sqmm",

            "specs": {
                "cross_section_mm2": size,
                "current_air": p.get("current_air"),
                "current_ground": p.get("current_ground"),
                "voltage_drop": p.get("voltage_drop")
            },

            "source": {
                "type": "catalogue",
                "page": p.get("source_page")
            }
        }

        db_products.append(db_product)

    # 🚨 IMPORTANT: clear old data (for testing)
    products_collection.delete_many({})

    if db_products:
        products_collection.insert_many(db_products)

    return {
        "inserted": len(db_products)
    }