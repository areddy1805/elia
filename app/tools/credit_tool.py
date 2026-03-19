import json
import os


class CreditBureauTool:

    def __init__(self):

        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        file_path = os.path.join(BASE_DIR, "data/external/credit_bureau.json")

        with open(file_path) as f:
            self.data = json.load(f)

    def get_credit_score(self, application_id: str) -> dict:
        record = self.data.get(application_id)

        if not record:
            return {
                "status": "NOT_FOUND",
                "cibil_score": None,
                "active_loans": None,
                "delinquencies": None
            }

        return {
            "status": "FOUND",
            **record
        }