from backend.catalogue.extractor import CatalogueExtractor
from backend.catalogue.parser import CatalogueParser

extractor = CatalogueExtractor()
parser = CatalogueParser()

file_path = "/Users/isha/PycharmProjects/AURA/data/datasheets/sample_cable.pdf"

data = extractor.extract(file_path)

products = parser.parse(data)

print(f"\n✅ TOTAL PRODUCTS EXTRACTED: {len(products)}\n")

for p in products[:10]:
    print(p)