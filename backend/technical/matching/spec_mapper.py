SPEC_MAPPING = {
    "voltage_kv": {
        "target": "voltage_drop",
        "type": "numeric_inverse"
    },
    "insulation_type": {
        "target": "material",
        "type": "categorical"
    },
    "standard": {
        "target": "standard",
        "type": "exact"
    }
}


def map_rfp_to_product(rfp_specs):
    mapped = {}

    for rfp_key, value in rfp_specs.items():
        if rfp_key in SPEC_MAPPING:
            mapping = SPEC_MAPPING[rfp_key]
            mapped[mapping["target"]] = {
                "value": value,
                "type": mapping["type"],
                "source": rfp_key
            }

    return mapped