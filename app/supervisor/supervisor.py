from app.state.loan_state import LoanApplicationState
from app.agents.intake_agent import IntakeAgent
from app.agents.risk_agent import RiskAgent
from app.agents.compliance_agent import ComplianceAgent
from app.evaluation.evaluator import Evaluator


class LoanSupervisor:

    def __init__(self):
        self.intake = IntakeAgent()
        self.risk = RiskAgent()
        self.compliance = ComplianceAgent()
        self.evaluator = Evaluator()

    def run(self, application: dict):

        state = LoanApplicationState(application)

        # -------------------
        # STEP 1: INTAKE
        # -------------------
        state = self.intake.process(state)

        if not self.is_valid(state):
            state.set_decision("REJECT", "Failed intake validation")
            return self.finalize(state)

        # -------------------
        # STEP 2: RISK
        # -------------------
        state = self.run_risk_with_retry(state)

        if self.is_analysis_failed(state):
            state.add_step("risk_failure", {
                "reason": "analysis incomplete after retries"
            })
            state.set_decision("MANUAL_REVIEW", "Unreliable risk analysis")
            return self.finalize(state)

        # -------------------
        # EARLY EXIT: HARD REJECT
        # -------------------
        if state.decision == "REJECT":
            state.add_step("early_exit", {
                "stage": "risk",
                "reason": "High risk rejection"
            })
            return self.finalize(state)

        # -------------------
        # STEP 3: COMPLIANCE
        # -------------------
        if state.decision == "APPROVE":
            state = self.compliance.process(state)

        return self.finalize(state)

    # =========================
    # FINALIZATION (CRITICAL)
    # =========================

    def finalize(self, state):
        state.set_confidence(self.compute_confidence(state))
        state = self.evaluator.evaluate(state)
        return state

    # =========================
    # VALIDATION
    # =========================

    def is_valid(self, state):
        last = state.steps[-1]
        return last["data"]["valid"]

    def is_analysis_failed(self, state):
        a = state.analysis

        if not a:
            return True

        required_fields = [
            "credit_score",
            "fraud_risk",
            "document_issue"
        ]

        for f in required_fields:
            if f not in a:
                return True

        return False

    # =========================
    # SAFE RETRY
    # =========================

    def run_risk_with_retry(self, state, max_retries=1):

        for attempt in range(max_retries + 1):

            temp_state = state.clone()
            temp_state = self.risk.process(temp_state)

            if not self.is_analysis_failed(temp_state):
                return temp_state

            state.add_step("risk_retry", {
                "attempt": attempt + 1
            })

        return state

    # =========================
    # CONFIDENCE ENGINE
    # =========================

    def compute_confidence(self, state):

        a = state.analysis

        if not a:
            return 0.0

        score = a.get("credit_score", 0)
        fraud = a.get("fraud_risk")
        delinquency = a.get("has_delinquency")

        confidence = 0.5

        if score > 750:
            confidence += 0.2
        elif score < 600:
            confidence += 0.1

        if fraud == "low":
            confidence += 0.2
        elif fraud == "high":
            confidence -= 0.2

        if delinquency is False:
            confidence += 0.1

        return round(max(0.0, min(confidence, 1.0)), 2)