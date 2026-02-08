import os
import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text without removing technical meaning.
    This function performs ONLY normalization (no summarization, no extraction).
    """

    if not text:
        return ""

    # Normalize excessive newlines (keep paragraph structure)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Normalize excessive spaces and tabs
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Remove standalone page numbers (lines containing only digits)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    return text.strip()


def clean_pages(pages: List[Dict]) -> List[Dict]:
    """
    Applies text cleaning to each extracted page while preserving page numbers.
    """

    cleaned_pages = []

    for page in pages:
        cleaned_pages.append({
            "page": page["page"],
            "text": clean_text(page["text"])
        })

    return cleaned_pages


# -------------------------------
# PHASE 2 MANUAL TEST (SAFE TEST)
# -------------------------------
if __name__ == "__main__":
    from backend.document_intelligence.ingestion.pdf_loader import load_pdf

    # Compute absolute project root
    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    # Absolute path to sample PDF
    pdf_path = os.path.join(PROJECT_ROOT, "data", "rfps", "sample_rfp.pdf")

    print("Looking for PDF at:", pdf_path)
    print("PDF exists:", os.path.exists(pdf_path))

    # Load and clean pages
    pages = load_pdf(pdf_path)
    cleaned_pages = clean_pages(pages)

    # Visual comparison (RAW vs CLEANED)
    print("\nRAW TEXT (first 500 chars):\n")
    print(pages[0]["text"][:500])

    print("\n" + "-" * 60 + "\n")

    print("CLEANED TEXT (first 500 chars):\n")
    print(cleaned_pages[0]["text"][:500])
