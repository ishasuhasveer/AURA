import pdfplumber
import io
import re
from backend.database.mongo_client import db


# ---------------- HELPERS ----------------

def is_number(value):
    try:
        float(value)
        return True
    except:
        return False


def clean_value(val):
    if val is None:
        return None
    return str(val).replace(",", "").strip()


def is_valid_price(value):
    return 10 <= value <= 10000000


def detect_product_type_from_table(table):
    """
    Detect product type per table (NOT per page)
    """
    text = " ".join(
        [cell for row in table for cell in row if cell]
    ).lower()

    if "zhfr" in text or "hffr" in text:
        return "ZHFR"
    elif "frls" in text:
        return "FRLS"
    elif "fr" in text:
        return "FR"

    return "UNKNOWN"


def extract_core_mapping(header_row):
    """
    Robust mapping: "2 CORE" → 2
    """
    core_map = {}

    for idx, col in enumerate(header_row):
        if not col:
            continue

        col = col.lower()

        match = re.search(r"(\d+)\s*c", col)
        if match:
            core_map[idx] = int(match.group(1))

    return core_map


def is_header_row(row):
    text = " ".join([c for c in row if c]).lower()
    return bool(re.search(r"\b\d+\s*core\b", text))


# ---------------- RULE EXTRACTION ----------------

def extract_pricing_rules(text: str):
    rules = []

    text = text.lower()

    matches = re.findall(
        r"(frls|zhfr|hffr|armour\w*|pvc|insulation)[^%]{0,50}?(\d+)\s*%",
        text
    )

    for keyword, percent in matches:

        if "frls" in keyword:
            rule_type = "frls_premium"
            product_type = "FRLS"

        elif "zhfr" in keyword or "hffr" in keyword:
            rule_type = "zhfr_premium"
            product_type = "ZHFR"

        elif "armour" in keyword:
            rule_type = "armouring"
            product_type = "ALL"

        elif "pvc" in keyword or "insulation" in keyword:
            rule_type = "insulation"
            product_type = "ALL"

        else:
            continue

        rules.append({
            "rule_type": rule_type,
            "product_type": product_type,
            "percentage": float(percent)
        })

    # deduplicate
    unique = {}
    for r in rules:
        key = (r["rule_type"], r["product_type"])
        unique[key] = r

    return list(unique.values())


# ---------------- MAIN LOADER ----------------

def load_pricing_from_pdf(file_bytes: bytes) -> int:

    inserted_count = 0
    rules_inserted = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        for page in pdf.pages:

            # ---------------- RULE EXTRACTION ----------------
            page_text = page.extract_text() or ""

            rules = extract_pricing_rules(page_text)

            for rule in rules:
                print("RULE DETECTED:", rule)

                db["pricing_rules"].update_one(
                    {
                        "rule_type": rule["rule_type"],
                        "product_type": rule["product_type"]
                    },
                    {"$set": rule},
                    upsert=True
                )

                rules_inserted += 1

            # ---------------- TABLE EXTRACTION ----------------
            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                if not table or len(table) < 2:
                    continue

                # Clean table
                table = [
                    [clean_value(cell) for cell in row]
                    for row in table
                ]

                # Detect product type per table
                product_type = detect_product_type_from_table(table)

                if product_type == "UNKNOWN":
                    print("⚠️ Skipping unknown table")
                    continue

                # Find header row
                header_row = None

                for row in table:
                    if is_header_row(row):
                        header_row = row
                        break

                if not header_row:
                    header_row = table[0]

                core_map = extract_core_mapping(header_row)

                if not core_map:
                    print("⚠️ No core mapping found")
                    continue

                header_found = False

                for row in table:

                    # Skip until header
                    if row == header_row:
                        header_found = True
                        continue

                    if not header_found:
                        continue

                    if not row or not is_number(row[0]):
                        continue

                    try:
                        cross_section = float(row[0])
                    except:
                        continue

                    # Validation
                    if cross_section <= 0 or cross_section > 1000:
                        continue

                    for col_idx, cores in core_map.items():

                        if col_idx >= len(row):
                            continue

                        cell = row[col_idx]

                        if not is_number(cell):
                            continue

                        price_per_100m = float(cell)

                        # Validate price
                        if not is_valid_price(price_per_100m):
                            print("❌ INVALID PRICE:", cell)
                            continue

                        price_per_meter = price_per_100m / 100

                        print(
                            f"INSERTING: {cross_section} sqmm | {cores}C | {product_type}"
                        )

                        db["pricing_catalog"].update_one(
                            {
                                "cross_section_mm2": cross_section,
                                "cores": cores,
                                "product_type": product_type
                            },
                            {
                                "$set": {
                                    "price_per_100m": price_per_100m,
                                    "price_per_meter": price_per_meter
                                }
                            },
                            upsert=True
                        )

                        inserted_count += 1

    print("\n✅ TOTAL PRICES INSERTED:", inserted_count)
    print("✅ TOTAL RULES INSERTED:", rules_inserted)

    return inserted_count