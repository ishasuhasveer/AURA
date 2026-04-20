import re
from typing import List, Dict, Any


class CatalogueParser:

    # --------------------------------------------------
    # MAIN FUNCTION
    # --------------------------------------------------
    def parse(self, extracted_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        all_products = []

        for page in extracted_pages:
            tables = page.get("tables", [])
            page_num = page.get("page")

            for table in tables:
                parsed_rows = self._parse_table(table, page_num)
                all_products.extend(parsed_rows)

        return all_products


    # --------------------------------------------------
    # TABLE PARSER
    # --------------------------------------------------
    def _parse_table(self, table: List[List[str]], page_num: int) -> List[Dict[str, Any]]:

        if not table or len(table) < 2:
            return []

        products = []

        for row in table:

            if not row or len(row) < 2:
                continue

            numbers = self._extract_clean_numbers(row)

            # 🚨 Reject noisy rows early
            if len(numbers) < 5:
                continue

            size = numbers[0]

            # 🚨 Skip garbage sizes
            if size > 1000 or size <= 0:
                continue

            # 🚨 Skip factor tables
            if numbers[1] < 10:
                continue

            current_air_vals = numbers[1:4]
            voltage_vals = numbers[4:7] if len(numbers) >= 7 else []

            # --------------------------------------------------
            # 🔥 EXTRACT CONFIG FROM TEXT (NEW)
            # --------------------------------------------------
            row_text = " ".join([str(c) for c in row]).lower()

            cores = self._extract_cores(row_text)
            conductor = self._extract_conductor(row_text)
            insulation = self._extract_insulation(row_text)
            armour = self._extract_armour(row_text)

            item = {
                "size_mm2": size,
                "current_air": max(current_air_vals) if current_air_vals else None,
                "voltage_drop": min(voltage_vals) if voltage_vals else None,
                "source_page": page_num,

                # 🔥 CONFIG (NO MORE HARD DEFAULTS)
                "insulation_type": insulation,
                "voltage_kv": 1.1,  # keep default (catalog usually fixed)
                "cores": cores,
                "conductor": conductor,
                "armour_type": armour,
                "standard": "IS8130"
            }

            if len(numbers) >= 10:
                item["current_ground"] = max(numbers[7:10])

            if self._is_valid_product(item):
                products.append(item)

        return products


    # --------------------------------------------------
    # CLEAN NUMBER EXTRACTION
    # --------------------------------------------------
    def _extract_clean_numbers(self, row):

        numbers = []

        for cell in row:
            matches = re.findall(r"\d+\.?\d*", str(cell))

            for m in matches:
                try:
                    val = float(m)

                    # 🚨 Remove garbage values
                    if val < 0.1 or val > 5000:
                        continue

                    numbers.append(val)

                except:
                    continue

        return numbers


    # --------------------------------------------------
    # 🔥 CONFIG EXTRACTION HELPERS (NEW)
    # --------------------------------------------------

    def _extract_cores(self, text):
        match = re.search(r"(\d+)\s*(core|c)", text)
        if match:
            return int(match.group(1))
        return 1  # safe default


    def _extract_conductor(self, text):
        if "al" in text:
            return "aluminium"
        if "cu" in text or "copper" in text:
            return "copper"
        return "copper"


    def _extract_insulation(self, text):
        if "pvc" in text:
            return "PVC"
        if "xlpe" in text:
            return "XLPE"
        return "XLPE"


    def _extract_armour(self, text):
        if "armoured" in text:
            return "ARMOURED"
        return "UNARMOURED"


    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------
    def _is_valid_product(self, item):

        size = item.get("size_mm2")
        current = item.get("current_air")
        voltage = item.get("voltage_drop")

        if size is None:
            return False

        valid_sizes = [
            1, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70,
            95, 120, 150, 185, 240, 300, 400, 500, 630
        ]

        if not any(abs(size - vs) < 0.5 for vs in valid_sizes):
            return False

        # Current sanity
        if current is None or current < 50 or current > 2000:
            return False

        # Voltage drop sanity
        if voltage is None or voltage <= 0 or voltage > 5:
            return False

        return True