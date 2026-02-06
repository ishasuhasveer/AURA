# backend/agents/sales_agent.py

import os
import re
from datetime import datetime
from backend.schemas.sales_schema import SalesAgentOutput


class SalesAgent:
    def __init__(self):
        pass

    def validate_file(self, file_path: str) -> None:
        if not file_path.lower().endswith(".pdf"):
            raise ValueError("Invalid file type. Only PDF files are allowed.")

        # NOTE: For API uploads, this path may not exist locally.
        # We will relax this later.
        # For now, comment this out to avoid false failures.
        # if not os.path.exists(file_path):
        #     raise FileNotFoundError("RFP file not found.")

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
        return ", ".join(found) if found else "General Electrical Supplies"

    def assign_priority(self, deadline: str) -> str:
        if deadline == "UNKNOWN":
            return "medium"

        try:
            deadline_date = datetime.strptime(deadline, "%d %B %Y")
            days_left = (deadline_date - datetime.now()).days
            return "high" if days_left <= 30 else "medium"
        except Exception:
            return "medium"

    def process_rfp(self, file_path: str, extracted_text: str) -> dict:
        self.validate_file(file_path)

        raw_output = {
            "rfp_id": self.generate_rfp_id(),
            "deadline": self.extract_deadline(extracted_text),
            "scope_summary": self.extract_scope(extracted_text),
            "priority": self.assign_priority(
                self.extract_deadline(extracted_text)
            )
        }

        validated = SalesAgentOutput.validate_output(raw_output)
        return validated.dict()