import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from the entire PDF with progress logging.
    Safe for large industrial catalogues.
    """
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages in PDF: {total_pages}")

        for i, page in enumerate(pdf.pages, start=1):
            print(f"Processing page {i}/{total_pages}...")
            text = page.extract_text()
            if text:
                pages_text.append(text)

    return "\n".join(pages_text)


if __name__ == "__main__":
    text = extract_text_from_pdf("data/datasheets/sample_cable.pdf")
    print("\n--- SAMPLE OUTPUT ---\n")
    print(text[:1500])
