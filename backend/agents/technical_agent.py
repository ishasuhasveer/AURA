from backend.database.mongo_client import db
from backend.technical.matching.spec_mapper import map_rfp_to_product


# --------------------------------------------------
# CLEAN HELPER
# --------------------------------------------------
def clean_value(val):
    if isinstance(val, str):
        return val.replace("\n", "").strip()
    return val


def suggest_sizes(voltage, sku_objects):
    if not voltage:
        return []

    sizes = sorted(list(set([
        sku.get("specs", {}).get("cross_section_mm2")
        for sku in sku_objects
    ])))

    if voltage >= 200:
        target = [95, 120, 150]
    elif voltage >= 100:
        target = [70, 95]
    else:
        target = []

    suggestions = []

    for t in target:
        for sku in sku_objects:
            if sku.get("specs", {}).get("cross_section_mm2") == t:
                suggestions.append({
                    "sku_id": sku.get("sku_id"),
                    "sku_config_id": sku.get("sku_config_id")
                })

    return suggestions


# --------------------------------------------------
# 🔥 HARD CONSTRAINT CHECK
# --------------------------------------------------
REQUIRED_CRITICAL = ["cross_section_mm2"]


def check_missing_critical(mapped_rfp):
    missing = []

    for param in REQUIRED_CRITICAL:
        if param not in mapped_rfp:
            missing.append(param)

    return missing


# --------------------------------------------------
# PARAM WEIGHTS
# --------------------------------------------------
PARAM_WEIGHTS = {
    "cross_section_mm2": 3.0,
    "current_air": 2.0,
    "voltage_kv": 2.0,
    "cores": 1.5,
    "insulation_type": 1.5,
    "flame_type": 1.0,
    "armour_type": 1.0,
    "conductor": 1.5,
    "standard": 1.0
}


# --------------------------------------------------
# MATCH FUNCTION
# --------------------------------------------------
def match_values(param, rfp_val, sku_val):

    if sku_val is None or sku_val == "UNKNOWN":
        return "Missing", 0

    # STRICT SIZE MATCH
    if param == "cross_section_mm2":
        return ("Exact", 1) if float(rfp_val) == float(sku_val) else ("Mismatch", 0)

    # NUMERIC MATCH
    if isinstance(rfp_val, (int, float)) and isinstance(sku_val, (int, float)):

        if sku_val >= rfp_val:
            return "Suitable", 1
        elif abs(sku_val - rfp_val) <= (0.15 * rfp_val):
            return "Approx", 0.5
        else:
            return "Undersized", 0

    # STRING MATCH
    rfp_val = str(rfp_val).lower()
    sku_val = str(sku_val).lower()

    if sku_val == rfp_val:
        return "Exact", 1

    # strict for critical fields
    if param in ["insulation_type", "conductor", "standard"]:
        return "Mismatch", 0

    if rfp_val in sku_val or sku_val in rfp_val:
        return "Partial", 0.5

    return "Mismatch", 0


# --------------------------------------------------
# MAIN TECHNICAL AGENT
# --------------------------------------------------
def run_technical_agent(nlp_output: dict) -> dict:

    raw_requirements = nlp_output.get("technical_requirements", {})
    requirements_list = nlp_output.get("requirements_list", [])

    if not requirements_list:
        if isinstance(raw_requirements, dict) and raw_requirements:
            requirements_list = [
                {"type": "generic", "use_case": "", "specs": raw_requirements}
            ]

    sku_objects = list(db["products"].find({}))

    if not sku_objects:
        return {"requirements_mapping": []}

    final_results = []

    for req in requirements_list:

        raw_rfp_spec = req.get("specs", {})
        use_case = req.get("use_case", "").lower()

        if not raw_rfp_spec:
            continue

        mapped_rfp = map_rfp_to_product(raw_rfp_spec)

        def fails_hard_constraints(mapped_rfp, sku_specs):

            # SIZE (mandatory)
            rfp_size = mapped_rfp.get("cross_section_mm2", {}).get("value")
            if rfp_size is not None:
                if sku_specs.get("cross_section_mm2") != rfp_size:
                    return True

            # CORES
            rfp_cores = mapped_rfp.get("cores", {}).get("value")
            if rfp_cores is not None:
                if sku_specs.get("cores") != rfp_cores:
                    return True

            # CONDUCTOR
            rfp_conductor = mapped_rfp.get("conductor", {}).get("value")
            if rfp_conductor:
                if sku_specs.get("conductor") != rfp_conductor:
                    return True

            # INSULATION (NEW)
            rfp_insulation = mapped_rfp.get("insulation_type", {}).get("value")
            if rfp_insulation:
                if sku_specs.get("insulation_type") != rfp_insulation:
                    return True

            # VOLTAGE (NEW)
            rfp_voltage = mapped_rfp.get("voltage_kv", {}).get("value")
            sku_voltage = sku_specs.get("voltage_kv")

            if rfp_voltage and sku_voltage:
                if sku_voltage < rfp_voltage:
                    return True

            return False

        print("🔥 MAPPED RFP:", mapped_rfp)

        # --------------------------------------------------
        # 🚨 STEP 1: CRITICAL VALIDATION (NEW FIX)
        # --------------------------------------------------
        missing = check_missing_critical(mapped_rfp)

        if missing:
            voltage = mapped_rfp.get("voltage_kv", {}).get("value")

            voltage_suggestions = suggest_sizes(voltage, sku_objects)

            # 🔥 SAFE: compute max size ONLY if DB exists
            max_size = 0

            try:
                max_size = max([
                    sku.get("specs", {}).get("cross_section_mm2", 0)
                    for sku in sku_objects
                ]) if sku_objects else 0
            except:
                max_size = 0

            return {
                "status": "missing_specs",

                "requirements_mapping": [],
                "recommended_skus": voltage_suggestions,
                "spec_match_scores": {},

                "error": f"Missing critical specs: {missing}",

                # ✅ FIXED ANALYSIS
                "analysis": {
                    "required_size": None,
                    "max_available_size": max_size,
                    "gap_ratio": None,
                    "insight": "Cannot determine feasibility without cable size"
                },

                "suggested_skus": voltage_suggestions,
                "recommendation": "Please specify cable size (sqmm) for accurate matching"
            }


        # --------------------------------------------------
        # 🚨 STEP 2: NORMAL MATCHING
        # --------------------------------------------------
        results = []
        seen_configs = set()

        for sku in sku_objects:

            sku_config_id = sku.get("sku_config_id")
            specs = sku.get("specs", {})
            description = sku.get("sku_name", "").lower()

            if fails_hard_constraints(mapped_rfp, specs):
                continue  # 🚨 CRITICAL FIX

            score = 0
            total_weight = 0
            row_table = []

            for param, meta in mapped_rfp.items():

                rfp_value = clean_value(meta["value"])
                sku_value = clean_value(specs.get(param, "UNKNOWN"))

                if rfp_value is None:
                    continue

                weight = PARAM_WEIGHTS.get(param, 1)

                match, points = match_values(param, rfp_value, sku_value)

                weighted_score = points * weight

                score += weighted_score
                total_weight += weight

                row_table.append({
                    "parameter": meta["source"],
                    "mapped_to": param,
                    "rfp_value": rfp_value,
                    "sku_value": sku_value,
                    "match": match,
                    "weight": weight,
                    "score": round(weighted_score, 2)
                })

            if use_case and use_case in description:
                score += 1

            match_percent = round((score / total_weight) * 100, 2) if total_weight > 0 else 0
            if match_percent < 50:
                continue

            config_id = sku.get("sku_config_id")

            if config_id in seen_configs:
                continue

            seen_configs.add(config_id)

            results.append({
                "sku_id": sku.get("sku_id"),
                "sku_config_id": config_id,
                "match_percent": match_percent,
                "table": row_table
            })

        # --------------------------------------------------
        # 🚨 STEP 3: NO MATCH CASE
        # --------------------------------------------------
        # --------------------------------------------------
        # 🚨 STEP 3: NO MATCH CASE (FIXED)
        # --------------------------------------------------
        if not results:

            response = build_intelligent_response(mapped_rfp, sku_objects)

            # 🚨 CRITICAL FIX: DO NOT TREAT SUGGESTIONS AS VALID SKUs
            response["recommended_skus"] = []  # ❌ remove misleading field

            # 🔥 Rename suggestions properly (closest matches only)
            response["closest_skus"] = response.get("suggested_skus", [])[:3]

            # Optional: clean duplicates
            seen = set()
            unique = []
            for s in response["closest_skus"]:
                sid = s.get("sku_config_id")
                if sid and sid not in seen:
                    seen.add(sid)
                    unique.append(s)

            response["closest_skus"] = unique

            # 🔥 Add label for UI clarity
            response["note"] = "Closest matches shown below do NOT fully satisfy requirements"

            return response

        results = sorted(
            results,
            key=lambda x: (x["match_percent"], x.get("sku_config_id")),
            reverse=True
        )

        final_results.append({
            "requirement": req,
            "matched_skus": results,
            "top_matches": results[:5]
        })

    return {
        "status": "success",
        "requirements_mapping": final_results
    }

def build_intelligent_response(mapped_rfp, sku_objects):

    required_size = mapped_rfp.get("cross_section_mm2", {}).get("value")
    voltage = mapped_rfp.get("voltage_kv", {}).get("value")

    all_sizes = [
        sku.get("specs", {}).get("cross_section_mm2", 0)
        for sku in sku_objects
        if sku.get("specs")
    ]

    max_size = max(all_sizes) if all_sizes else None

    # ---------------- SUGGEST CLOSEST ----------------
    sorted_skus = sorted(
        sku_objects,
        key=lambda x: (
            - (x.get("specs", {}).get("cross_section_mm2", 0) or 0)
        )
    )

    seen = set()
    suggestions = []

    voltage_suggestions = suggest_sizes(voltage, sku_objects)

    for sku in sorted_skus:
        sid = sku.get("sku_config_id")

        if sid in seen:
            continue

        seen.add(sid)

        suggestions.append({
            "sku_id": sku.get("sku_id"),
            "sku_config_id": sku.get("sku_config_id"),
            "size": sku.get("specs", {}).get("cross_section_mm2")
        })

        if len(suggestions) >= 3:
            break

    # ---------------- ANALYSIS ----------------
    analysis = {
        "required_size": required_size,
        "max_available_size": max_size,
        "gap_ratio": round(required_size / max_size, 2) if required_size and max_size else None
    }

    return {
        "requirements_mapping": [],
        "recommended_skus": suggestions,
        "spec_match_scores": {},

        "error": "No SKU satisfies technical constraints",

        "analysis": analysis,

        "suggested_skus": suggestions + voltage_suggestions,

        "recommendation": "Consider custom manufacturing or parallel cable configuration",
        "status": "no_match"
    }