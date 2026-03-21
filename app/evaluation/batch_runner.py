import os
import json
import time
from app.supervisor.supervisor import LoanSupervisor


class BatchEvaluator:

    def __init__(self):
        self.supervisor = LoanSupervisor()

        self.data_path = "data/applications"
        self.gt_path = "data/ground_truth.json"

        with open(self.gt_path) as f:
            self.ground_truth = json.load(f)

    def run(self):

        total = 0
        correct = 0
        manual = 0
        missed = 0

        latencies = []

        for app_id in sorted(os.listdir(self.data_path)):

            app_file = f"{self.data_path}/{app_id}/application.json"

            if not os.path.exists(app_file):
                continue

            with open(app_file) as f:
                application = json.load(f)

            # -------------------
            # LATENCY START
            # -------------------
            start = time.time()

            state = self.supervisor.run(application)

            latency = time.time() - start
            latencies.append(latency)

            # -------------------
            # RESULTS
            # -------------------
            actual = state.decision
            expected = self.ground_truth[app_id]["decision"]

            total += 1

            if actual == expected:
                correct += 1
            elif actual == "MANUAL_REVIEW":
                manual += 1
                missed += 1
            else:
                missed += 1

            print("\n============================")
            print(f"APP ID: {app_id}")
            print(f"EXPECTED: {expected}")
            print(f"ACTUAL: {actual}")
            print(f"LATENCY: {round(latency, 3)} sec")
            print("============================\n")

        # -------------------
        # AGGREGATE LATENCY
        # -------------------
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        print("\n===== METRICS =====\n")
        print(f"Total: {total}")
        print(f"Accuracy: {round(correct / total, 2)}")
        print(f"Manual Reviews: {manual}")
        print(f"Missed Decisions: {missed}")

        print("\n===== LATENCY =====\n")
        print(f"Avg Latency: {round(avg_latency, 3)} sec")
        print(f"Max Latency: {round(max_latency, 3)} sec")
        print(f"Min Latency: {round(min_latency, 3)} sec")