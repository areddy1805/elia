# ELIA - Loan Underwriting Multi-Agent System

![Python](https://img.shields.io/badge/python-3.11-blue)
![Architecture](https://img.shields.io/badge/architecture-multi--agent-orange)
![Type](https://img.shields.io/badge/system-Applied%20AI-purple)
![Domain](https://img.shields.io/badge/domain-BFSI-green)
![LLM](https://img.shields.io/badge/LLM-Ollama%20Local-black)
![Model](https://img.shields.io/badge/model-llama3.2%3A3b-yellow)
![Decision Engine](https://img.shields.io/badge/engine-rule%20%2B%20scoring-red)
![Explainability](https://img.shields.io/badge/XAI-Enabled-brightgreen)
![Evaluation](https://img.shields.io/badge/evaluation-batch%20tested-blueviolet)
![Status](https://img.shields.io/badge/status-stable-success)

Overview

This system simulates a real-world loan underwriting engine used in BFSI environments. It combines:
• Deterministic business rules
• LLM-assisted analysis
• Document parsing
• Multi-agent orchestration
• Evaluation + explainability

The system processes loan applications end-to-end and produces:

{
"decision": "APPROVE | REJECT | MANUAL_REVIEW",
"reason": { ...structured explanation... },
"confidence": 0.0–1.0,
"steps": [audit trail]
}

⸻

1. System Architecture

High-Level Flow

Application Input
↓
[Supervisor]
↓
[Intake Agent] → Validation
↓
[Risk Agent]
├─ External Tools (Credit, Fraud)
├─ Document Parsing (Regex + LLM)
├─ Consistency Checker
├─ LLM Analysis
└─ Decision Engine
↓
[Compliance Agent]
↓
Confidence + Evaluation
↓
Final Decision + Audit Trail

⸻

2. Project Structure

elia/
│
├── app/
│ ├── agents/
│ │ ├── intake_agent.py
│ │ ├── risk_agent.py
│ │ └── compliance_agent.py
│ │
│ ├── supervisor/
│ │ └── supervisor.py
│ │
│ ├── tools/
│ │ ├── credit_tool.py
│ │ └── fraud_tool.py
│ │
│ ├── documents/
│ │ ├── document_loader.py
│ │ ├── llm_parser.py
│ │ ├── consistency_checker.py
│ │ └── parsers/
│ │ ├── bank_parser.py
│ │ └── salary_parser.py
│ │
│ ├── state/
│ │ └── state.py
│ │
│ ├── prompts/
│ │ └── prompt_analysis.py
│ │
│ └── evaluation/
│ ├── evaluator.py
│ └── batch_runner.py
│
├── data/
│ ├── applications/
│ ├── documents/
│ ├── external/
│ └── ground_truth.json
│
├── scripts/
│ ├── run_single.py
│ └── run_batch.py
│
├── requirements.txt
└── README.md

⸻

3. Core Components

3.1 Supervisor (Orchestrator)

Controls full pipeline.

Responsibilities:
• Execution flow control
• Retry handling
• Early exits
• Confidence scoring

Supervisor = Workflow Engine

⸻

3.2 Agents

Intake Agent
• Validates input structure
• Ensures required fields

Risk Agent (Core Engine)

Handles:
• Tool integration
• Document parsing
• LLM reasoning
• Decision logic

This is the brain of the system.

⸻

Compliance Agent
• Applies policy overrides
• Final gate before output

⸻

4. Data Sources

4.1 Application Data

{
"applicant": {...},
"employment": {...},
"loan": {...}
}

⸻

4.2 External Tools

Credit Tool

{
"cibil_score": 760,
"active_loans": 1
}

Fraud Tool

{
"fraud_risk": "low",
"document_tampering": false
}

⸻

4.3 Documents

Located in:

data/documents/{application_id}/

Types:
• bank_statement.txt
• employment.txt

⸻

5. Document Processing Pipeline

Step 1 — Load

DocumentLoader → raw text

⸻

Step 2 — Regex Parsing (Fast Path)

BankStatementParser
SalarySlipParser

⸻

Step 3 — LLM Parsing (Fallback)

Triggered only if:

missing / incomplete fields

⸻

Step 4 — Merge Strategy

Regex result = base
LLM result = override (only if non-null)

⸻

Step 5 — Consistency Check

Produces flags:

salary_vs_application_mismatch
salary_vs_bank_mismatch
cashflow_instability

⸻

6. Decision Engine

Multi-Layer Logic

Layer 1 — Hard Reject

- score < 600
- fraud detected
- extreme loan ratio

⸻

Layer 2 — Strong Approve

- score > 720
- low fraud
- high income strength
- low ratio

⸻

Layer 3 — Medium Risk Reject

- low score + high burden

⸻

Layer 4 — Consistency Logic

soft → penalize
strong → manual review

⸻

Layer 5 — Borderline Rules

- moderate income
- high ratio

⸻

Layer 6 — Weighted Scoring (Final)

score_weight = aggregated signal score

Decision:

> = 6 → APPROVE
> <= 2 → REJECT
> else → MANUAL

⸻

7. Explainability

Each decision includes:

{
"factors": {...},
"rules_triggered": [...],
"summary": "reason"
}

⸻

Example

{
"rules_triggered": ["strong_profile"],
"summary": "All approval conditions satisfied"
}

⸻

8. State Management

All data flows through:

LoanApplicationState

Tracks:
• application
• tool outputs
• parsed docs
• analysis
• decision
• steps (audit trail)

⸻

9. Evaluation System

Batch Evaluation

python scripts/run_batch.py

Metrics:

Accuracy
False Approvals (critical)
False Rejections
Manual Reviews
Missed Decisions

⸻

Example Output

Total: 5
Accuracy: 0.8
False Approvals: 0
Manual Reviews: 0

⸻

10. Performance Optimizations

Implemented

1. Document Caching

self.doc_cache[application_id]

Avoids repeated parsing.

⸻

2. LLM Fallback Only

LLM used only when regex fails

⸻

3. Deterministic Decision Layer

No LLM in final decision

⸻

11. Key Design Decisions

1. Hybrid System

LLM = feature extraction
Rules = decision

⸻

2. Explainability First

Every decision is traceable.

⸻

3. Conservative Bias

Avoid false approvals > maximize accuracy

⸻

4. Separation of Concerns

Agents / Tools / Documents / Decision isolated

⸻

12. Known Limitations

1. Small dataset
1. Limited document formats
1. No real-time external APIs
1. No historical credit depth

⸻

13. Future Improvements

1. Add liabilities + EMI aggregation
1. Add bureau history (multi-loan trends)
1. Add vector DB for document retrieval
1. Replace rules with ML model (optional)
1. Add API layer (FastAPI)
1. Add async processing
1. Add logging + monitoring

⸻

14. System Classification

Type: Applied AI System
Category: Decision Intelligence / BFSI
Level: Production-style simulation

⸻

15. Final Summary

This system replicates:

Real-world loan underwriting pipeline with:

- multi-agent orchestration
- hybrid AI + rules
- document intelligence
- explainable decisions
- evaluation framework

It is not a demo.

It is a simplified production architecture.
