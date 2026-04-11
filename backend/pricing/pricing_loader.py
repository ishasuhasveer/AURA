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


def is_valid_price(value):
    return 10 <= value <= 10000000


# ---------------- TEXT EXTRACTION (ROBUST) ----------------

def extract_rows_from_text(text: str):
    lines = text.split("\n")
    valid_rows = []

    for line in lines:
        nums = re.findall(r"\d+\.?\d*", line)

        # At least 5 numbers → real pricing row
        if len(nums) >= 5:
            valid_rows.append(nums)

    return valid_rows


def split_row(nums):
    first = nums[0]

    for i in range(1, len(nums)):
        if nums[i] == first:
            return nums[:i], nums[i:]

    return nums, []


def process_side(nums, cable_type):
    results = []

    if not nums:
        return results

    cross_section = float(nums[0])
    prices = nums[1:]

    core_labels = [1, 2, 3, 3.5, 4]

    for i, price in enumerate(prices):
        if i >= len(core_labels):
            break

        if not is_number(price):
            continue

        val = float(price)

        if not is_valid_price(val):
            continue

        results.append({
            "cross_section_mm2": cross_section,
            "cores": float(core_labels[i]),
            "product_type": "FRLS",   # default safe
            "cable_type": cable_type,
            "price_per_meter": val,
            "price_per_100m": val * 100
        })

    return results


def parse_rows(rows):
    results = []

    for nums in rows:
        left, right = split_row(nums)

        results.extend(process_side(left, "UNARMOURED"))

        if right:
            results.extend(process_side(right, "ARMOURED"))

    return results


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

        else:
            rule_type = "misc"
            product_type = "ALL"

        rules.append({
            "rule_type": rule_type,
            "product_type": product_type,
            "percentage": float(percent)
        })

    return rules


# ---------------- MAIN LOADER ----------------

def load_pricing_from_pdf(file_bytes: bytes) -> int:

    db["pricing_catalog"].delete_many({})  # 🔥 clean insert

    inserted_count = 0
    rules_inserted = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        for page in pdf.pages:

            text = page.extract_text() or ""

            print("\n--- PAGE ---")
            print(text[:200])

            # -------- RULES --------
            rules = extract_pricing_rules(text)

            for r in rules:
                db["pricing_rules"].update_one(
                    {"rule_type": r["rule_type"], "product_type": r["product_type"]},
                    {"$set": r},
                    upsert=True
                )
                rules_inserted += 1

            # -------- TEXT PARSING --------
            rows = extract_rows_from_text(text)
            print("ROWS FOUND:", len(rows))

            parsed = parse_rows(rows)
            print("PARSED:", len(parsed))

            for row in parsed:
                db["pricing_catalog"].update_one(
                    {
                        "cross_section_mm2": row["cross_section_mm2"],
                        "cores": row["cores"],
                        "product_type": row["product_type"],
                        "cable_type": row["cable_type"]
                    },
                    {"$set": row},
                    upsert=True
                )
                inserted_count += 1

    print("\n✅ INSERTED:", inserted_count)
    print("✅ RULES:", rules_inserted)

    return inserted_count