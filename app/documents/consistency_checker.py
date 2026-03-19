class ConsistencyChecker:

    def analyze(self, application, bank, salary):

        income = application["employment"]["monthly_income"]

        doc_salary = salary.get("declared_salary")
        bank_salary = bank.get("salary_detected")

        neg_months = bank.get("negative_months", 0)
        total_months = bank.get("total_months", 1)

        neg_ratio = (neg_months / total_months) if total_months else 0

        flags = []

        # -------------------
        # INCOME MISMATCH
        # -------------------
        if doc_salary and income:
            diff = abs(doc_salary - income) / income
            if diff > 0.25:
                flags.append("salary_vs_application_mismatch")

        if bank_salary and income:
            diff = abs(bank_salary - income) / income
            if diff > 0.3:
                flags.append("bank_vs_application_mismatch")

        # -------------------
        # INTERNAL INCONSISTENCY
        # -------------------
        if doc_salary and bank_salary:
            diff = abs(doc_salary - bank_salary) / doc_salary
            if diff > 0.3:
                flags.append("salary_vs_bank_mismatch")

        # -------------------
        # CASH FLOW RISK
        # -------------------
        if neg_ratio > 0.4:
            flags.append("cashflow_instability")

        return {
            "flags": flags,
            "neg_ratio": round(neg_ratio, 2)
        }