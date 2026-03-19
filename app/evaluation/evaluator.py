import json


class Evaluator:

    def __init__(self):
        with open("data/ground_truth.json") as f:
            self.gt = json.load(f)

    def evaluate(self, state):

        app_id = state.application_id

        expected = self.gt.get(app_id, {}).get("decision")

        if not expected:
            state.set_evaluation(False, "UNKNOWN_GT")
            return state

        correct = (expected == state.decision)

        state.set_evaluation(correct, expected)

        return state