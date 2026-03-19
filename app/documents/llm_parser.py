import json
import ollama


class LLMDocumentParser:

    def __init__(self, model="mistral:7b-instruct"):
        self.model = model

    def parse_bank(self, text: str):

        prompt = f"""
Extract structured financial signals from this bank statement.

Return ONLY valid JSON.

Required format:
{{
  "salary_detected": number or null,
  "avg_balance": number or null,
  "negative_balance_months": number,
  "total_months": number
}}

Text:
{text}
"""

        return self._run(prompt)

    def parse_salary(self, text: str):

        prompt = f"""
Extract salary from this salary slip.

Return ONLY valid JSON.

Format:
{{
  "declared_salary": number or null
}}

Text:
{text}
"""

        return self._run(prompt)

    def _run(self, prompt):

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response["message"]["content"]

        try:
            return json.loads(content)
        except:
            start = content.find("{")
            end = content.rfind("}")

            if start != -1 and end != -1:
                try:
                    return json.loads(content[start:end+1])
                except:
                    pass

        return {}