# backend/agents/sales_agent.py

import os
import re
from datetime import datetime, timedelta
from typing import Dict

class SalesAgent:
    def __init__(self):
        pass

def validate_file(self, file_path: str) -> None:
    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Invalid file type. Only PDF files are allowed.")

    if not os.path.exists(file_path):
        raise FileNotFoundError("RFP file not found.")

def generate_rfp_id(self) -> str:
    today = datetime.now().strftime("%Y%m%d")
    return f"RFP-{today}"

def extract_deadline(self, text: str) -> str:
    match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
    if match:
        return match.group(1)
    return "UNKNOWN"


def extract_scope(self, text: str) -> str:
    keywords = [
        "cable",
        "wire",
        "conductor",
        "electrical",
        "fmeg",
        "switchgear"
    ]

    found = [k for k in keywords if k.lower() in text.lower()]

    if found:
        return ", ".join(found)
    return "General Electrical Supplies"

def assign_priority(self, deadline: str) -> str:
    if deadline == "UNKNOWN":
        return "medium"

    try:
        deadline_date = datetime.strptime(deadline, "%d %B %Y")
        days_left = (deadline_date - datetime.now()).days

        if days_left <= 30:
            return "high"
        return "medium"

    except Exception:
        return "medium"


def process_rfp(self, file_path: str, extracted_text: str) -> Dict:
    self.validate_file(file_path)

    rfp_id = self.generate_rfp_id()
    deadline = self.extract_deadline(extracted_text)
    scope = self.extract_scope(extracted_text)
    priority = self.assign_priority(deadline)

    return {
        "rfp_id": rfp_id,
        "deadline": deadline,
        "scope_summary": scope,
        "priority": priority
    }

if __name__ == "__main__":
    agent = SalesAgent()
    dummy_text = """
    This RFP is issued for supply of electrical cables.
    Submission deadline: 15 February 2026
    """

    result = agent.process_rfp("sample.pdf", dummy_text)
    print(result)
