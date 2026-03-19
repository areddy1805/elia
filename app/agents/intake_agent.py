class IntakeAgent:

    def process(self, state):
        app = state.application

        issues = []

        if not app.get("applicant"):
            issues.append("Missing applicant info")

        if not app.get("employment"):
            issues.append("Missing employment info")

        if not app.get("loan"):
            issues.append("Missing loan info")

        result = {
            "valid": len(issues) == 0,
            "issues": issues
        }

        state.add_step("intake_validation", result)

        return state