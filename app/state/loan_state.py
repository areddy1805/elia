class LoanApplicationState:

    def __init__(self, application: dict):
        self.application = application
        self.application_id = application["application_id"]

        # tool outputs
        self.credit_data = None
        self.fraud_data = None

        # analysis
        self.analysis = None

        # final decision
        self.decision = None
        self.reason = None

        # trace
        self.steps = []
        
        #  observability
        self.confidence = None
        self.correct = None

    # -----------------------
    # STATE MUTATIONS
    # -----------------------

    def add_step(self, step_name: str, data: dict):
        self.steps.append({
            "step": step_name,
            "data": data
        })

    def set_credit_data(self, data: dict):
        self.credit_data = data
        self.add_step("credit_check", data)

    def set_fraud_data(self, data: dict):
        self.fraud_data = data
        self.add_step("fraud_check", data)

    def set_analysis(self, analysis: dict):
        self.analysis = analysis
        self.add_step("risk_analysis", analysis)

    def set_decision(self, decision: str, reason: dict):
        self.decision = decision
        self.reason = reason

        self.add_step("final_decision", {
            "decision": decision,
            "reason": reason
        })
    
    def set_confidence(self, score: float):
        self.confidence = score
        self.add_step("confidence_score", {
            "score": score
        })

    def set_evaluation(self, correct: bool, expected: str):
        self.correct = correct
        self.add_step("evaluation", {
            "correct": correct,
            "expected": expected,
            "actual": self.decision
        })

    # -----------------------
    # CLONING (CRITICAL FIX)
    # -----------------------

    def clone(self):
        import copy
        return copy.deepcopy(self)

    # -----------------------
    # EXPORT
    # -----------------------

    def to_dict(self):
        return {
            "application_id": self.application_id,
            "application": self.application,
            "credit_data": self.credit_data,
            "fraud_data": self.fraud_data,
            "analysis": self.analysis,
            "decision": self.decision,
            "reason": self.reason,
            "steps": self.steps,
            "confidence": self.confidence,
            "correct": self.correct,
        }