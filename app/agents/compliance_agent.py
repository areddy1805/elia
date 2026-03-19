class ComplianceAgent:

    def process(self, state):

        decision = state.decision
        app = state.application
        analysis = state.analysis

        income = app["employment"]["monthly_income"]
        loan_amount = app["loan"]["amount"]

        issues = []
        override = None
        reason = None

        # -----------------------
        # RULE 1: Loan-to-Income Ratio
        # -----------------------
        if income:
            ratio = loan_amount / (income * 12)

            if ratio > 10:
                override = "REJECT"
                reason = "Loan amount too high relative to income"
                issues.append("High loan-to-income ratio")

            elif ratio > 6:
                override = "MANUAL_REVIEW"
                reason = "Borderline loan-to-income ratio"
                issues.append("Moderate loan-to-income risk")

        # -----------------------
        # RULE 2: Delinquency Check
        # -----------------------
        if analysis.get("has_delinquency"):
            override = "MANUAL_REVIEW"
            reason = "Past delinquency detected"
            issues.append("Delinquency history")

        # -----------------------
        # APPLY OVERRIDE
        # -----------------------
        if override:
            state.set_decision(override, reason)

        state.add_step("compliance_check", {
            "issues": issues,
            "override_applied": bool(override)
        })

        return state