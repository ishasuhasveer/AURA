from backend.technical.datasheets.pdf_parser import extract_text_from_pdf
from decision_intelligence.datasheet_extractor import extract_sku_from_text
from decision_intelligence.normalization import normalize_sku

text = extract_text_from_pdf("data/datasheets/sample_cable.pdf")

sku = extract_sku_from_text(
    text=text,
    sku_id="SAMPLE_CABLE_001",
    source_doc="sample_cable.pdf"
)

sku = normalize_sku(sku)

print(sku)
