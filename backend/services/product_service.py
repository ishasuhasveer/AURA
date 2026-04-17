import os

from backend.technical.datasheets.pdf_parser import (
    extract_text_from_pdf,
    extract_sku_from_text
)

from backend.technical.datasheets.segmenter import (
    split_catalogue_into_products
)

from backend.database.collections_db import products_collection


async def process_catalogue_upload(file):

    # -------------------------------
    # STEP 1: Save file temporarily
    # -------------------------------
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    # -------------------------------
    # STEP 2: Extract text from PDF
    # -------------------------------
    text = extract_text_from_pdf(temp_path)

    # -------------------------------
    # STEP 3: Split into product blocks
    # -------------------------------
    blocks = split_catalogue_into_products(text)

    products = []

    # -------------------------------
    # STEP 4: Extract SKUs
    # -------------------------------
    for i, block in enumerate(blocks):

        sku = extract_sku_from_text(
            block,
            sku_id=f"{file.filename}_SKU_{i}",
            source_doc=file.filename
        )

        # -------------------------------
        # STEP 5: Normalize for DB
        # -------------------------------
        db_product = {
            "sku_name": sku["sku_id"],
            "specs": {
                "voltage_kv": sku.get("voltage"),
                "conductor_material": sku.get("conductor"),
                "insulation_type": sku.get("insulation"),
                "standard": sku.get("standard"),
                "core_count": sku["attributes"].get("core_count"),
                "cross_section_mm2": sku["attributes"].get("cross_section_mm2"),
                "armouring": sku["attributes"].get("armouring")
            },
            "source_document": sku.get("source_doc")
        }

        # -------------------------------
        # STEP 6: Basic validation
        # -------------------------------
        if db_product["specs"]["voltage_kv"] is None:
            continue

        products.append(db_product)

    # -------------------------------
    # STEP 7: Insert into MongoDB
    # -------------------------------
    if products:
        products_collection.insert_many(products)

    # -------------------------------
    # STEP 8: Cleanup
    # -------------------------------
    os.remove(temp_path)

    return {
        "message": "Catalogue processed",
        "total_blocks": len(blocks),
        "inserted_products": len(products)
    }