import re


def normalize_whitespace(text: str) -> str:
    """
    Replace newlines and multiple spaces with a single space.
    """
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_voltage(voltage: str):
    if not voltage:
        return None
    voltage = normalize_whitespace(voltage)
    return voltage


def normalize_standard(standard: str):
    if not standard:
        return None
    standard = normalize_whitespace(standard).upper()
    return standard


def normalize_simple_text(value: str):
    if not value:
        return None
    return normalize_whitespace(value).upper()


def normalize_sku(sku: dict) -> dict:
    """
    Normalize extracted SKU fields without changing meaning.
    """
    sku["voltage"] = normalize_voltage(sku.get("voltage"))
    sku["standard"] = normalize_standard(sku.get("standard"))
    sku["conductor"] = normalize_simple_text(sku.get("conductor"))
    sku["insulation"] = normalize_simple_text(sku.get("insulation"))

    return sku
