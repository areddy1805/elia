import os
import json
import random
from datetime import datetime, timedelta
import shutil

BASE_PATH = "data"
APP_PATH = os.path.join(BASE_PATH, "applications")
DOC_PATH = os.path.join(BASE_PATH, "documents")
EXT_PATH = os.path.join(BASE_PATH, "external")


# -----------------------------
# RESET (CLEAN STATE)
# -----------------------------
def reset_data():
    if os.path.exists(BASE_PATH):
        shutil.rmtree(BASE_PATH)

    os.makedirs(APP_PATH, exist_ok=True)
    os.makedirs(DOC_PATH, exist_ok=True)
    os.makedirs(EXT_PATH, exist_ok=True)


# -----------------------------
# HELPERS
# -----------------------------
def rand_date():
    start = datetime(2025, 1, 1)
    return (start + timedelta(days=random.randint(0, 400))).strftime("%Y-%m-%d")


def rand_name():
    first = ["Priya", "Rahul", "Amit", "Sneha", "Karan", "Neha", "Arjun"]
    last = ["Sharma", "Reddy", "Verma", "Patel", "Singh"]
    return f"{random.choice(first)} {random.choice(last)}"


def rand_company():
    return random.choice(["Infosys", "TCS", "Wipro", "Accenture", "HCL"])


# -----------------------------
# SEGMENTS
# -----------------------------
def get_segments():
    segments = (
        ["strong"] * 12 +
        ["reject"] * 10 +
        ["borderline"] * 10 +
        ["edge"] * 8
    )
    random.shuffle(segments)
    return segments


# -----------------------------
# CREDIT
# -----------------------------
def generate_credit(segment):

    if segment == "strong":
        score = random.randint(730, 820)
        return {"cibil_score": score, "active_loans": random.randint(0, 2), "delinquencies": 0}

    if segment == "reject":
        score = random.randint(500, 640)
        return {"cibil_score": score, "active_loans": random.randint(2, 5), "delinquencies": random.randint(1, 3)}

    if segment == "borderline":
        score = random.randint(650, 720)
        return {"cibil_score": score, "active_loans": random.randint(1, 4), "delinquencies": random.choice([0, 1])}

    score = random.randint(680, 750)
    return {"cibil_score": score, "active_loans": random.randint(2, 5), "delinquencies": random.randint(0, 2)}


# -----------------------------
# FRAUD
# -----------------------------
def generate_fraud(segment):

    if segment == "strong":
        return {"name_mismatch": False, "document_tampering": False, "ip_risk": "low"}

    if segment == "reject":
        return {"name_mismatch": True, "document_tampering": random.choice([True, False]), "ip_risk": random.choice(["medium", "high"])}

    if segment == "edge":
        return {"name_mismatch": True, "document_tampering": True, "ip_risk": "high"}

    return {"name_mismatch": False, "document_tampering": False, "ip_risk": random.choice(["low", "medium"])}


# -----------------------------
# APPLICATION
# -----------------------------
def generate_application(app_id, segment):

    name = rand_name()
    income = random.randint(30000, 150000)

    if segment == "strong":
        loan = random.randint(200000, 900000)
    elif segment == "reject":
        loan = random.randint(1200000, 2500000)
    else:
        loan = random.randint(500000, 1500000)

    return {
        "application_id": app_id,
        "applicant": {
            "name": name,
            "age": random.randint(23, 55),
            "pan": f"PAN{app_id[-3:]}XYZ",
            "aadhaar": "XXXX-XXXX-1234"
        },
        "employment": {
            "type": random.choice(["salaried", "self_employed"]),
            "employer": rand_company(),
            "monthly_income": income,
            "years_experience": random.randint(1, 12)
        },
        "loan": {
            "amount": loan,
            "tenure_months": random.choice([24, 36, 48, 60]),
            "purpose": random.choice(["home", "car", "personal", "business"])
        },
        "metadata": {
            "submitted_at": rand_date(),
            "channel": random.choice(["web", "mobile_app"])
        }
    }


# -----------------------------
# DOCUMENTS
# -----------------------------
def generate_bank(income, segment):

    balances = [random.randint(20000, 80000) for _ in range(3)]

    if segment == "reject":
        balances = [random.randint(-5000, 20000) for _ in range(3)]

    salary_lines = ""
    if segment != "reject":
        salary_lines = "\n".join([
            f"Salary credited: {income} on 1 Jan",
            f"Salary credited: {income} on 1 Feb",
            f"Salary credited: {income} on 1 Mar"
        ])

    return f"""Account Holder: User
Bank: SBI

Jan Closing Balance: {balances[0]}
Feb Closing Balance: {balances[1]}
Mar Closing Balance: {balances[2]}

{salary_lines}

EMI: {random.randint(5000, 20000)} (loan)

Note: {"Salary consistent" if segment == "strong" else "Irregular activity"}
"""


def generate_employment(income, segment, name):

    if segment == "reject" and random.random() > 0.5:
        return ""

    noisy_income = income

    if segment == "borderline":
        noisy_income = int(income * random.uniform(0.6, 1.4))

    return f"""Employee Name: {name}
Company: {rand_company()} Limited

Status: Active

Monthly Salary: {int(noisy_income/1000)}k (approx)
Joining Year: {random.randint(2015, 2022)}
"""


# -----------------------------
# GROUND TRUTH
# -----------------------------
def assign_gt(credit, fraud, app):

    score = credit["cibil_score"]
    delinquency = credit["delinquencies"]
    income = app["employment"]["monthly_income"]
    loan = app["loan"]["amount"]

    ratio = loan / (income * 12)

    if score > 720 and delinquency == 0 and fraud["ip_risk"] == "low" and ratio < 6:
        return "APPROVE", "Strong credit, consistent income signals, no fraud"

    if score < 600 or delinquency > 1 or fraud["name_mismatch"] or ratio > 12:
        return "REJECT", "Poor credit / fraud / high risk profile"

    return "MANUAL_REVIEW", "Borderline or inconsistent signals"


# -----------------------------
# MAIN
# -----------------------------
def main():

    reset_data()

    ground_truth = {}
    credit_data = {}
    fraud_data = {}

    segments = get_segments()

    for i in range(1, 41):

        app_id = f"APP{i:03}"
        segment = segments[i - 1]

        app = generate_application(app_id, segment)
        credit = generate_credit(segment)
        fraud = generate_fraud(segment)

        decision, reason = assign_gt(credit, fraud, app)

        # SAVE APPLICATION
        app_dir = os.path.join(APP_PATH, app_id)
        os.makedirs(app_dir, exist_ok=True)

        with open(os.path.join(app_dir, "application.json"), "w") as f:
            json.dump(app, f, indent=2)

        # SAVE DOCUMENTS
        doc_dir = os.path.join(DOC_PATH, app_id)
        os.makedirs(doc_dir, exist_ok=True)

        with open(os.path.join(doc_dir, "bank_statement.txt"), "w") as f:
            f.write(generate_bank(app["employment"]["monthly_income"], segment))

        with open(os.path.join(doc_dir, "employment.txt"), "w") as f:
            f.write(generate_employment(
                app["employment"]["monthly_income"],
                segment,
                app["applicant"]["name"]
            ))

        # STORE GLOBAL DATA
        credit_data[app_id] = credit
        fraud_data[app_id] = fraud

        ground_truth[app_id] = {
            "decision": decision,
            "reason": reason
        }

    # SAVE GLOBAL FILES
    with open(os.path.join(BASE_PATH, "ground_truth.json"), "w") as f:
        json.dump(ground_truth, f, indent=2)

    with open(os.path.join(EXT_PATH, "credit_bureau.json"), "w") as f:
        json.dump(credit_data, f, indent=2)

    with open(os.path.join(EXT_PATH, "fraud_signals.json"), "w") as f:
        json.dump(fraud_data, f, indent=2)


if __name__ == "__main__":
    main()