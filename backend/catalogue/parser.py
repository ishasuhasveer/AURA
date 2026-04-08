import re
from typing import List, Dict, Any


class CatalogueParser:
    """
    Converts extracted PDF tables into structured product data.
    Designed for industrial cable catalogues.
    """

    # ---------------- MAIN FUNCTION ----------------
    def parse(self, extracted_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        all_products = []

        for page in extracted_pages:
            tables = page.get("tables", [])
            page_num = page.get("page")

            for table in tables:
                parsed_rows = self._parse_table(table, page_num)
                all_products.extend(parsed_rows)

        return all_products

    # ---------------- TABLE PARSER ----------------
    def _parse_table(self, table: List[List[str]], page_num: int) -> List[Dict[str, Any]]:

        if not table or len(table) < 2:
            return []

        products = []

        for row in table:

            if not row or len(row) < 2:
                continue

            # Try to extract numeric values
            numbers = []

            for cell in row:
                nums = re.findall(r"\d+\.?\d*", str(cell))
                if nums:
                    val = float(nums[0])

                    # Ignore tiny junk numbers
                    if val < 0.1:
                        continue

                    numbers.append(val)

            # We expect rows like:
            # [size, voltage_drop, current_air, size2, voltage_drop2, current_ground]

            if len(numbers) >= 7:

                size = numbers[0]

                # Detect if it's real current table
                # If numbers[1] is too small → it's NOT current table
                if numbers[1] < 10:
                    continue  # skip factor tables

                current_air_vals = numbers[1:4]
                voltage_vals = numbers[4:7]

                item = {
                    "size_mm2": size,
                    "current_air": max(current_air_vals),
                    "voltage_drop": min(voltage_vals),
                    "source_page": page_num
                }

                if len(numbers) >= 10:
                    item["current_ground"] = max(numbers[7:10])

                if self._is_valid_product(item):
                    products.append(item)

                print("RAW NUMBERS:", numbers)

        return products

    # ---------------- HEADER MAPPING ----------------
    def _map_headers(self, headers: List[str]) -> List[str]:

        mapped = []

        for h in headers:
            h_clean = (h or "").lower()

            # SIZE
            if "size" in h_clean or "area" in h_clean or "mm2" in h_clean:
                mapped.append("size_mm2")

            # CURRENT (AIR)
            elif "current" in h_clean and "air" in h_clean:
                mapped.append("current_air")

            # CURRENT (GROUND)
            elif "current" in h_clean and "ground" in h_clean:
                mapped.append("current_ground")

            # VOLTAGE DROP
            elif "voltage" in h_clean and "drop" in h_clean:
                mapped.append("voltage_drop")

            # GENERIC CURRENT
            elif "current" in h_clean:
                mapped.append("current_rating")

            else:
                mapped.append(None)

        return mapped

    # ---------------- VALUE CLEANING ----------------
    def _clean_value(self, value: str, key: str):

        if value is None:
            return None

        value = value.strip()

        if value == "":
            return None

        # Extract numeric values
        if key in [
            "size_mm2",
            "current_rating",
            "current_air",
            "current_ground",
            "voltage_drop"
        ]:
            nums = re.findall(r"\d+\.?\d*", value)
            return float(nums[0]) if nums else None

        if key == "core_count":
            nums = re.findall(r"\d+", value)
            return int(nums[0]) if nums else None

        return value

    # ---------------- VALIDATION ----------------
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

        if size not in valid_sizes:
            return False

        # Current must be realistic
        if current is None or current < 50 or current > 2000:
            return False

        # Voltage drop sanity
        if voltage is None or voltage <= 0 or voltage > 5:
            return False

        return True