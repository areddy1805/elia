import re


class SalarySlipParser:

    def parse(self, text):

        if not text:
            return {"declared_salary": None}

        # Match patterns like:
        # 82k, 82,000, 82000
        match = re.search(r'(\d{2,3}(?:,\d{3})?)(\s*k)?', text, re.IGNORECASE)

        if match:
            number = match.group(1).replace(",", "")
            value = int(number)

            # Handle "k"
            if match.group(2):
                value *= 1000

            return {"declared_salary": value}

        return {"declared_salary": None}