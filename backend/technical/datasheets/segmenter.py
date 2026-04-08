import re


def split_catalogue_into_products(text: str):
    blocks = re.split(r"\n\s*\n", text)

    product_blocks = []

    for block in blocks:
        cleaned = block.strip()

        # Must contain at least 1 key signal
        if len(cleaned) < 100:
            continue

        if not re.search(r"(kV|KV|mm2|XLPE|PVC|Core)", cleaned, re.IGNORECASE):
            continue

        product_blocks.append(cleaned)

    return product_blocks