import re


class SalarySlipParser:

    def parse(self, text: str):

        match = re.search(r"salary\s*[:\-]?\s*(\d+)", text.lower())

        salary = int(match.group(1)) if match else None

        return {
            "declared_salary": salary
        }