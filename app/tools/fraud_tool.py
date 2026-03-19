import json
import os


class FraudDetectionTool:

    def __init__(self):
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        file_path = os.path.join(BASE_DIR, "data/external/fraud_signals.json")

        with open(file_path) as f:
            self.data = json.load(f)

    def check_fraud(self, application_id: str) -> dict:
        record = self.data.get(application_id)

        if not record:
            return {
                "status": "NOT_FOUND",
                "name_mismatch": None,
                "document_tampering": None,
                "ip_risk": None
            }

        return {
            "status": "FOUND",
            **record
        }