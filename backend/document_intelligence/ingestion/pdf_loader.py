import os
import pdfplumber
from typing import List, Dict


def load_pdf(pdf_path: str) -> List[Dict]:
    """
    Load a PDF file and extract text page-wise.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        List[Dict]: A list of dictionaries with page number and text.
                    Example:
                    [
                        {"page": 1, "text": "..."},
                        {"page": 2, "text": "..."}
                    ]
    """
    pages_content = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_content.append({
                "page": page_number,
                "text": text
            })

    return pages_content


if __name__ == "__main__":
    # PRINT DEBUG INFO
    print("Current file:", __file__)

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    print("Computed project root:", PROJECT_ROOT)

    sample_pdf_path = os.path.join(PROJECT_ROOT, "data", "sample_rfp.pdf")

    print("Looking for PDF at:", sample_pdf_path)
    print("PDF exists:", os.path.exists(sample_pdf_path))

    extracted_pages = load_pdf(sample_pdf_path)

    print(f"Total pages extracted: {len(extracted_pages)}")
    print(extracted_pages[0])
