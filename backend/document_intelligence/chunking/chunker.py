from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_sections(sections: Dict[str, str],
                   chunk_size: int = 500,
                   chunk_overlap: int = 50) -> Dict[str, List[str]]:
    """
    Chunk each RFP section independently to preserve semantic meaning.
    """

    chunked_sections = {}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    for section_name, section_text in sections.items():
        if not section_text:
            chunked_sections[section_name] = []
            continue

        chunks = splitter.split_text(section_text)
        chunked_sections[section_name] = chunks

    return chunked_sections
if __name__ == "__main__":
    import os
    from backend.document_intelligence.ingestion.pdf_loader import load_pdf
    from backend.document_intelligence.preprocessing.cleaner import clean_pages
    from backend.document_intelligence.sectioning.section_detector import detect_sections

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    pdf_path = os.path.join(PROJECT_ROOT, "data", "rfps", "sample_rfp.pdf")

    pages = load_pdf(pdf_path)
    cleaned_pages = clean_pages(pages)
    sections = detect_sections(cleaned_pages)

    chunked = chunk_sections(sections)

    print("\n====== CHUNK SUMMARY ======\n")
    for section, chunks in chunked.items():
        print(f"{section}: {len(chunks)} chunks")
        if chunks:
            print("Sample chunk:\n", chunks[0][:300])
            print("-" * 50)
