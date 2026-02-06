from typing import Dict, Any, Optional


def empty_rfp_spec(rfp_id: str) -> Dict[str, Any]:
    """
    Create an empty normalized RFP technical specification object.

    This schema mirrors the SKU schema structurally, enabling
    deterministic, field-by-field compliance comparison.

    Fields are populated ONLY when explicitly stated in the RFP.
    No defaults. No inference.
    """

    return {
        "rfp_id": rfp_id,

        # -------- Mandatory technical requirements --------
        "voltage": None,
        "conductor": None,
        "insulation": None,
        "standard": None,

        # -------- Optional technical requirements --------
        "attributes": {
            "core_count": None,
            "cross_section_mm2": None,
            "armouring": None
        }
    }
