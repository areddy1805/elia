import re


class BankStatementParser:

    def parse(self, text: str):

        balances = re.findall(r"Balance:\s*(-?\d+)", text)
        balances = [int(b) for b in balances]

        salary_mentions = re.findall(r"salary\s*[:\-]?\s*(\d+)", text.lower())
        salary = int(salary_mentions[0]) if salary_mentions else None

        return {
            "avg_balance": sum(balances)/len(balances) if balances else None,
            "min_balance": min(balances) if balances else None,
            "salary_detected": salary,
            "balance_trend": "negative" if any(b < 0 for b in balances) else "stable",
            "negative_months": sum(1 for b in balances if b < 0),
            "total_months": len(balances)
        }