import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from typing import List, Dict, Any


class CatalogueExtractor:
    """
    Extracts text + tables from catalogue PDFs.

    Handles:
    1. Text-based PDFs (KEI type)
    2. Image-based PDFs (Polycab type via OCR)
    """

    def __init__(self, ocr_enabled: bool = True):
        self.ocr_enabled = ocr_enabled

    # ---------------- MAIN ENTRY ----------------
    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract full PDF into structured raw format.
        """
        results = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):

                text = page.extract_text()
                tables = page.extract_tables()

                # If no text → fallback to OCR
                if (not text or text.strip() == "") and self.ocr_enabled:
                    text = self._extract_text_with_ocr(file_path, page_num)

                results.append({
                    "page": page_num,
                    "raw_text": text,
                    "tables": tables
                })

        return results

    # ---------------- OCR FALLBACK ----------------
    def _extract_text_with_ocr(self, file_path: str, page_num: int) -> str:
        """
        Use OCR for image-based PDFs.
        """
        try:
            images = convert_from_path(
                file_path,
                first_page=page_num,
                last_page=page_num
            )

            if not images:
                return ""

            image = images[0]
            text = pytesseract.image_to_string(image)

            return text

        except Exception as e:
            print(f"OCR failed on page {page_num}: {e}")
            return ""