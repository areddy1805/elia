def build_analysis_prompt(application_json: str, credit_data: str, fraud_data: str) -> str:
    return f"""
You are a risk analysis system.

Extract structured risk signals.

DO NOT make final decision.

RETURN ONLY JSON.

----------------------

APPLICATION:
{application_json}

CREDIT:
{credit_data}

FRAUD:
{fraud_data}

----------------------

OUTPUT FORMAT:

{{
  "credit_score": <number>,
  "has_delinquency": <true/false>,
  "fraud_risk": "<low/medium/high>",
  "document_issue": <true/false>,
  "income_strength": "<low/medium/high>"
}}
"""