import json
import ollama

from app.tools.credit_tool import CreditBureauTool
from app.tools.fraud_tool import FraudDetectionTool
from app.prompts.prompt_analysis import build_analysis_prompt

from app.documents.document_loader import DocumentLoader
from app.documents.parsers.bank_parser import BankStatementParser
from app.documents.parsers.salary_parser import SalarySlipParser
from app.documents.llm_parser import LLMDocumentParser
from app.documents.consistency_checker import ConsistencyChecker


class RiskAgent:

    def __init__(self, model="llama3.2:3b", use_llm_docs=True):
        self.model = model
        self.use_llm_docs = use_llm_docs

        self.credit_tool = CreditBureauTool()
        self.fraud_tool = FraudDetectionTool()

        self.doc_loader = DocumentLoader()
        self.bank_parser = BankStatementParser()
        self.salary_parser = SalarySlipParser()
        self.llm_parser = LLMDocumentParser()
        self.consistency_checker = ConsistencyChecker()

        # CACHE (critical for performance)
        self.doc_cache = {}

    def process(self, state):

        app_id = state.application_id

        # -------------------
        # TOOL DATA
        # -------------------
        credit_data = self.credit_tool.get_credit_score(app_id)
        fraud_data = self.fraud_tool.check_fraud(app_id)

        state.set_credit_data(credit_data)
        state.set_fraud_data(fraud_data)

        # -------------------
        # DOCUMENT PARSING (CACHED + HYBRID)
        # -------------------
        if app_id in self.doc_cache:
            bank_data, salary_data = self.doc_cache[app_id]
        else:
            docs = self.doc_loader.load_documents(app_id)

            raw_bank = docs.get("bank_statement.txt", "")
            raw_salary = docs.get("salary_slip.txt", "")

            # REGEX FIRST (fast path)
            bank_data = self.bank_parser.parse(raw_bank)
            salary_data = self.salary_parser.parse(raw_salary)

            # LLM FALLBACK ONLY IF NEEDED
            if self.use_llm_docs:

                # Bank fallback
                if not bank_data.get("salary_detected") or not bank_data.get("total_months"):
                    llm_bank = self.llm_parser.parse_bank(raw_bank)
                    bank_data.update({k: v for k, v in llm_bank.items() if v is not None})

                # Salary fallback
                if not salary_data.get("declared_salary"):
                    llm_salary = self.llm_parser.parse_salary(raw_salary)
                    salary_data.update({k: v for k, v in llm_salary.items() if v is not None})

            # Cache result
            self.doc_cache[app_id] = (bank_data, salary_data)

        state.add_step("document_parsing", {
            "bank": bank_data,
            "salary": salary_data
        })

        # -------------------
        # CONSISTENCY CHECK (SINGLE SOURCE OF TRUTH)
        # -------------------
        consistency = self.consistency_checker.analyze(
            state.application,
            bank_data,
            salary_data
        )

        state.add_step("consistency_check", consistency)

        # -------------------
        # LLM ANALYSIS (CORE)
        # -------------------
        analysis = self.run_analysis(state.application, credit_data, fraud_data)
        state.set_analysis(analysis)

        # -------------------
        # DECISION
        # -------------------
        decision, reason = self.make_decision(state)
        state.set_decision(decision, reason)

        return state

    def run_analysis(self, application, credit_data, fraud_data):

        prompt = build_analysis_prompt(
            json.dumps(application, indent=2),
            json.dumps(credit_data, indent=2),
            json.dumps(fraud_data, indent=2)
        )

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response["message"]["content"])

    # -----------------------
    # FINAL DECISION ENGINE
    # -----------------------
    def make_decision(self, state):

        a = state.analysis
        application = state.application

        # CORE SIGNALS
        score = a.get("credit_score")
        fraud = a.get("fraud_risk")
        doc_issue = a.get("document_issue")
        delinquency = a.get("has_delinquency")
        income_strength = a.get("income_strength")

        income = application["employment"]["monthly_income"]
        loan_amount = application["loan"]["amount"]

        ratio = loan_amount / (income * 12) if income else None

        # DOCUMENT SIGNALS (only for explainability, NOT direct decisions)
        doc_step = next(
            (s["data"] for s in state.steps if s["step"] == "document_parsing"),
            {}
        )

        bank = doc_step.get("bank", {})
        salary_doc = doc_step.get("salary", {})

        doc_salary = salary_doc.get("declared_salary")
        bank_salary = bank.get("salary_detected")

        neg_months = bank.get("negative_months", 0)
        total_months = bank.get("total_months", 0)
        neg_ratio = (neg_months / total_months) if total_months else 0

        diff_ratio = None
        if doc_salary and income:
            diff_ratio = abs(doc_salary - income) / income

        # CONSISTENCY SIGNALS (PRIMARY DOCUMENT LOGIC)
        consistency = next(
            (s["data"] for s in state.steps if s["step"] == "consistency_check"),
            {}
        )

        flags = consistency.get("flags", [])

        # FACTORS (FOR EXPLAINABILITY)
        factors = {
            "credit_score": score,
            "fraud_risk": fraud,
            "delinquency": delinquency,
            "income_strength": income_strength,
            "loan_to_income_ratio": round(ratio, 2) if ratio else None,
            "declared_income": income,
            "salary_from_slip": doc_salary,
            "salary_from_bank": bank_salary,
            "negative_month_ratio": round(neg_ratio, 2),
            "salary_diff_ratio": round(diff_ratio, 2) if diff_ratio else None,
            "consistency_flags": flags
        }

        rules = []

        # -------------------
        # HARD REJECT
        # -------------------
        if score is None:
            return "MANUAL_REVIEW", {
                "factors": factors,
                "rules_triggered": ["missing_credit_score"],
                "summary": "Missing credit score"
            }

        if score < 600:
            rules.append("low_credit_score")
            return "REJECT", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Credit score below threshold"
            }

        if fraud == "high" or doc_issue:
            rules.append("fraud_detected")
            return "REJECT", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Fraud risk detected"
            }

        if ratio and ratio > 12:
            rules.append("extreme_loan_ratio")
            return "REJECT", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Loan too large relative to income"
            }

        # -------------------
        # CONSISTENCY RULES (ALL DOCUMENT LOGIC HERE)
        # -------------------
        if "salary_vs_application_mismatch" in flags:
            rules.append("income_mismatch")
            return "MANUAL_REVIEW", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Income mismatch across sources"
            }

        if "salary_vs_bank_mismatch" in flags:
            rules.append("cross_source_mismatch")
            return "MANUAL_REVIEW", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Mismatch between salary slip and bank records"
            }

        if "cashflow_instability" in flags:
            rules.append("cashflow_instability")
            return "MANUAL_REVIEW", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Unstable cash flow pattern"
            }

        # -------------------
        # STRONG APPROVE
        # -------------------
        if (
            score > 720 and
            fraud == "low" and
            not delinquency and
            ratio and ratio < 6 and
            income_strength == "high"
        ):
            rules.append("strong_profile")
            return "APPROVE", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "All approval conditions satisfied"
            }

        # -------------------
        # BORDERLINE
        # -------------------
        if ratio and ratio > 8:
            rules.append("high_ratio")
            return "MANUAL_REVIEW", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "High loan-to-income ratio"
            }

        if income_strength == "medium":
            rules.append("moderate_income")
            return "MANUAL_REVIEW", {
                "factors": factors,
                "rules_triggered": rules,
                "summary": "Moderate income strength"
            }

        return "MANUAL_REVIEW", {
            "factors": factors,
            "rules_triggered": ["insufficient_confidence"],
            "summary": "Not enough strong signals"
        }