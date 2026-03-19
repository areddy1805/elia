import os
import json
from collections import Counter

from app.supervisor.supervisor import LoanSupervisor


DATA_PATH = "data/applications"
GT_PATH = "data/ground_truth.json"


class BatchEvaluator:

    def __init__(self):
        self.supervisor = LoanSupervisor()

        with open(GT_PATH) as f:
            self.gt = json.load(f)

    def run(self):

        results = []

        for file in os.listdir(DATA_PATH):
            if not file.endswith(".json"):
                continue

            with open(os.path.join(DATA_PATH, file)) as f:
                app = json.load(f)

            state = self.supervisor.run(app)

            results.append({
                "app_id": state.application_id,
                "predicted": state.decision,
                "expected": self.gt.get(state.application_id, {}).get("decision"),
                "confidence": state.confidence
            })

        self.compute_metrics(results)

    # ------------------------
    # METRICS
    # ------------------------

    def compute_metrics(self, results):

        total = len(results)

        correct = 0
        false_approve = 0
        false_reject = 0
        manual_review = 0
        missed_decisions = 0  # NEW

        for r in results:

            pred = r["predicted"]
            exp = r["expected"]

            if pred == exp:
                correct += 1

            elif pred == "APPROVE" and exp == "REJECT":
                false_approve += 1

            elif pred == "REJECT" and exp == "APPROVE":
                false_reject += 1

            elif pred == "MANUAL_REVIEW":
                manual_review += 1
                if exp in ["APPROVE", "REJECT"]:
                    missed_decisions += 1

        print("\n===== METRICS =====\n")

        print(f"Total: {total}")
        print(f"Accuracy: {round(correct/total, 2)}")

        print(f"False Approvals (CRITICAL): {false_approve}")
        print(f"False Rejections: {false_reject}")

        print(f"Manual Reviews: {manual_review}")
        print(f"Missed Decisions: {missed_decisions}")

if __name__ == "__main__":
    BatchEvaluator().run()