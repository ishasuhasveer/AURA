from backend.catalogue.extractor import CatalogueExtractor
from backend.catalogue.parser import CatalogueParser
from backend.database.collections_db import products_collection


# --------------------------------------------------
# NORMALIZATION HELPERS
# --------------------------------------------------

def safe_float(val, default=None):
    try:
        return float(val)
    except:
        return default


def safe_int(val, default=None):
    try:
        return int(float(val))
    except:
        return default


def normalize_conductor(val):
    if not val:
        return "copper"

    val = str(val).lower()

    if "al" in val:
        return "aluminium"
    if "cu" in val or "copper" in val:
        return "copper"

    return "copper"


def normalize_insulation(val):
    if not val:
        return "XLPE"

    val = str(val).upper()

    if "PVC" in val:
        return "PVC"
    if "XLPE" in val:
        return "XLPE"

    return "XLPE"


def normalize_flame_type(val):
    if not val:
        return "NORMAL"

    val = str(val).upper()

    if "FRLS" in val:
        return "FRLS"
    if "FR" in val:
        return "FR"

    return "NORMAL"


def normalize_armour(val):
    if not val:
        return "UNARMOURED"

    val = str(val).upper()

    if "ARMOURED" in val:
        return "ARMOURED"

    return "UNARMOURED"


# --------------------------------------------------
# SKU CONFIG KEY (CRITICAL)
# --------------------------------------------------

def generate_sku_config_id(specs):
    return f"{specs['conductor']}_{specs['insulation_type']}_{specs['cores']}C_{specs['cross_section_mm2']}"


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def process_catalogue(file_path: str):

    extractor = CatalogueExtractor()
    parser = CatalogueParser()

    print("📄 Extracting catalogue...")
    extracted = extractor.extract(file_path)

    print("🧠 Parsing catalogue...")
    products = parser.parse(extracted)

    print(f"✅ Clean products parsed: {len(products)}")

    db_products = []

    for p in products:

        size = safe_int(p.get("size_mm2"))
        if not size:
            continue

        cores = safe_int(p.get("cores"), 1)
        conductor = normalize_conductor(p.get("conductor"))
        insulation = normalize_insulation(p.get("insulation_type"))
        flame_type = normalize_flame_type(p.get("insulation_type"))
        armour = normalize_armour(p.get("cable_type"))

        # ---------------- NORMALIZED SPEC BLOCK ----------------
        specs = {
            "cross_section_mm2": size,
            "current_air": safe_float(p.get("current_air")),
            "current_ground": safe_float(p.get("current_ground")),
            "voltage_drop": safe_float(p.get("voltage_drop")),

            # 🔥 CRITICAL MATCHING FIELDS
            "insulation_type": insulation,
            "flame_type": flame_type,
            "voltage_kv": safe_float(p.get("voltage_kv"), 1.1),
            "cores": cores,
            "conductor": conductor,
            "armour_type": armour,
            "standard": str(p.get("standard", "IS8130")).upper()
        }

        # 🔑 CONFIG ID (LINK TO PRICING)
        sku_config_id = generate_sku_config_id(specs)

        # 🆔 UNIQUE SKU (NO COLLISION)
        sku_id = f"{sku_config_id}"

        db_product = {
            "sku_id": sku_id,
            "sku_name": f"{conductor.upper()} {insulation} Cable {size} sqmm {cores}C",

            "sku_config_id": sku_config_id,

            "specs": specs,

            "product_metadata": {
                "category": "cable",
                "application": "power",
                "unit_type": "meter",              # 🔥 CRITICAL FIX
                "pricing_basis": "length"          # 🔥 CRITICAL FIX
            },

            "source": {
                "type": "catalogue",
                "page": p.get("source_page")
            }
        }

        print(f"📦 INSERT PREVIEW: {db_product}")

        db_products.append(db_product)

    # --------------------------------------------------
    # RESET COLLECTION (DEV MODE)
    # --------------------------------------------------
    print("🧹 Clearing old products...")
    products_collection.delete_many({})

    if db_products:
        print(f"🚀 Inserting {len(db_products)} products...")
        products_collection.insert_many(db_products)

    print("✅ Catalogue ingestion complete")

    return {
        "inserted": len(db_products)
    }