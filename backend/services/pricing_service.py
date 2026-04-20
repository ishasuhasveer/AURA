import pandas as pd
from backend.database.collections_db import pricing_collection


# --------------------------------------------------
# NORMALIZATION HELPERS (MATCH PRODUCT SIDE)
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
# SKU CONFIG ID (MUST MATCH PRODUCT LOGIC)
# --------------------------------------------------

def generate_sku_config_id(conductor, insulation, cores, size):
    return f"{conductor}_{insulation}_{cores}C_{size}"


# --------------------------------------------------
# MAIN PRICING INGESTION
# --------------------------------------------------

def process_pricing(file_path: str):

    print("📄 Loading pricing file...")
    df = pd.read_csv(file_path)

    db_pricing = []

    for _, row in df.iterrows():

        size = safe_int(row.get("cross_section_mm2"))
        if not size:
            continue

        cores = safe_int(row.get("cores"), 1)
        conductor = normalize_conductor(row.get("conductor"))
        insulation = normalize_insulation(row.get("insulation_type"))
        flame_type = normalize_flame_type(row.get("product_type"))
        armour = normalize_armour(row.get("cable_type"))

        price_per_100m = safe_float(row.get("price_per_100m"))
        price_per_meter = safe_float(row.get("price_per_meter"))

        # 🔥 Ensure per meter pricing
        if not price_per_meter and price_per_100m:
            price_per_meter = price_per_100m / 100

        if not price_per_meter:
            continue  # skip invalid rows

        # 🔑 CONFIG ID (SAME AS PRODUCT)
        sku_config_id = generate_sku_config_id(
            conductor,
            insulation,
            cores,
            size
        )

        pricing_doc = {
            "sku_config_id": sku_config_id,

            # 🔧 MATCHING FIELDS
            "cross_section_mm2": size,
            "cores": cores,
            "conductor": conductor,
            "insulation_type": insulation,
            "flame_type": flame_type,
            "armour_type": armour,

            # 💰 PRICING
            "price_per_meter": price_per_meter,
            "price_per_100m": price_per_meter * 100,

            # 📦 META
            "unit_type": "meter",
            "pricing_basis": "length"
        }

        print(f"💰 INSERT PREVIEW: {pricing_doc}")

        db_pricing.append(pricing_doc)

    # --------------------------------------------------
    # RESET COLLECTION (DEV MODE)
    # --------------------------------------------------
    print("🧹 Clearing old pricing...")
    pricing_collection.delete_many({})

    if db_pricing:
        print(f"🚀 Inserting {len(db_pricing)} pricing records...")
        pricing_collection.insert_many(db_pricing)

    print("✅ Pricing ingestion complete")

    return {
        "inserted": len(db_pricing)
    }