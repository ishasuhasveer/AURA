# backend/agents/sales_agent.py

import re
import uuid
from datetime import datetime, date
from backend.schemas.sales_schema import SalesAgentOutput


class SalesAgent:

    def generate_rfp_id(self) -> str:
        return f"RFP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

    def extract_deadline(self, text: str):
        match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d %B %Y").date()
            except Exception:
                return None
        return None

    def extract_scope(self, text: str) -> str:
        keywords = [
            "cable",
            "wire",
            "conductor",
            "electrical",
            "fmeg",
            "switchgear"
        ]

        found = list(set([k for k in keywords if k.lower() in text.lower()]))
        return ", ".join(found) if found else "General Electrical Supplies"

    def assign_priority(self, deadline: date) -> str:
        """
        Assign priority based on deadline proximity.
        """

        if not deadline:
            return "medium"

        try:
            today = datetime.now().date()
            days_left = (deadline - today).days

            if days_left < 0:
                return "low"
            elif days_left <= 30:
                return "high"
            else:
                return "medium"

        except Exception:
            return "medium"

    def process_rfp(self, file_name: str, extracted_text: str) -> dict:

        deadline = self.extract_deadline(extracted_text)

        raw_output = {
            "rfp_id": self.generate_rfp_id(),
            "deadline": deadline,  # must be date object
            "scope_summary": self.extract_scope(extracted_text),
            "priority": self.assign_priority(deadline)
        }

        validated = SalesAgentOutput.validate_output(raw_output)
        return validated.dict()