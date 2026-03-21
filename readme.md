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

ELIA is a production-style loan underwriting system that simulates real BFSI decision pipelines using:
• Deterministic risk policies
• LLM-assisted feature extraction
• Document intelligence
• Multi-agent orchestration
• Async execution + evaluation framework

⸻

Output Contract

{
"decision": "APPROVE | REJECT | MANUAL_REVIEW",
"reason": {
"factors": {},
"rules_triggered": [],
"summary": ""
},
"confidence": 0.0,
"latency_sec": 0.0,
"steps": []
}

⸻

1. System Architecture

End-to-End Flow

Application Input
↓
Supervisor
↓
Intake Agent
↓
Risk Agent
├── Credit Tool
├── Fraud Tool
├── Document Pipeline
├── Consistency Engine
├── LLM Analysis
└── Decision Engine
↓
Compliance Agent
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
│ ├── evaluation/
│ │ ├── evaluator.py
│ │ └── batch_runner.py
│ │
│ └── queue/ # async processing (Celery)
│
├── data/
│ ├── applications/
│ ├── documents/
│ ├── external/
│ │ ├── credit_bureau.json
│ │ └── fraud_signals.json
│ └── ground_truth.json
│
├── scripts/
│ ├── generate_dataset.py
│ ├── run_single.py
│ └── run_batch.py
│
├── requirements.txt
└── README.md

⸻

3. Core Components

3.1 Supervisor (Workflow Engine)

Controls execution pipeline.

Responsibilities:
• Agent orchestration
• Retry logic
• Failure isolation
• Confidence scoring

⸻

3.2 Agents

Intake Agent
• Validates schema
• Rejects malformed inputs

⸻

Risk Agent (Core Engine)

Responsible for:
• Tool integration
• Document parsing
• Consistency validation
• LLM-based analysis
• Deterministic decision

⸻

Compliance Agent
• Policy enforcement
• Override layer
• Final validation

⸻

4. Data Sources

4.1 Application

application.json

Structured input (employment, loan, applicant).

⸻

4.2 External Signals

Credit Bureau

data/external/credit_bureau.json

cibil_score
active_loans
delinquencies

⸻

Fraud Signals

data/external/fraud_signals.json

name_mismatch
document_tampering
ip_risk

⸻

4.3 Documents

data/documents/{APP_ID}/

    •	bank_statement.txt
    •	employment.txt

⸻

5. Document Intelligence Pipeline

Stage 1 — Load

Raw text ingestion

⸻

Stage 2 — Regex Parsing (Primary)
• Bank parser
• Salary parser

Fast, deterministic extraction

⸻

Stage 3 — LLM Fallback

Triggered only when:
• missing values
• low confidence extraction

⸻

Stage 4 — Merge Strategy

regex → base
llm → override (non-null only)

⸻

Stage 5 — Consistency Engine

Generates flags:
• salary_vs_application_mismatch
• salary_vs_bank_mismatch
• cashflow_instability

⸻

6. Decision Engine

Strict layered logic.

⸻

Layer 1 — Hard Reject
• credit score < 600
• fraud signals
• extreme loan ratio

⸻

Layer 2 — Strong Approve
• score > 720
• low fraud
• no delinquencies
• ratio < 6

⸻

Layer 3 — Consistency Rules
• cross-source mismatch → manual
• instability → manual

⸻

Layer 4 — Borderline Handling
• moderate income
• high ratio

⸻

Layer 5 — Final Decision

APPROVE / REJECT / MANUAL_REVIEW

No LLM used here.

⸻

7. Explainability (XAI)

Every decision includes:

factors
rules_triggered
summary

Full traceability.

⸻

8. State Management

Central object:

LoanApplicationState

Tracks:
• application
• tool outputs
• document outputs
• analysis
• decision
• audit steps

⸻

9. Evaluation Framework

Batch Execution

python scripts/run_batch.py

⸻

Metrics
• Accuracy
• False Approvals (critical)
• False Rejections
• Manual Reviews
• Missed Decisions

⸻

Example

Total: 40
Accuracy: 0.82
False Approvals: 0
Manual Reviews: 6

⸻

10. Dataset System

Synthetic dataset generator:

python scripts/generate_dataset.py

⸻

Coverage
• Strong profiles
• Reject cases
• Borderline cases
• Edge fraud cases

⸻

Guarantees
• Consistent schema
• Tool-compatible format
• Document variability
• Controlled distribution

⸻

11. Performance Optimizations

1. Document Cache

doc_cache[app_id]

Avoids repeated parsing.

⸻

2. Selective LLM Usage

LLM only used when required.

⸻

3. Deterministic Decision Layer

Zero LLM in final decision.

⸻

4. Async Processing (Celery)
   • Background execution
   • Task polling API
   • Latency isolation

⸻

12. API Layer (FastAPI)

Endpoints

Submit (Async)

POST /evaluate-loan-async

⸻

Fetch Result

GET /result/{task_id}

⸻

Decision Logs

GET /decisions

⸻

13. Failure Handling
    • Retry in supervisor
    • Timeout protection (LLM)
    • Null-safe data normalization
    • Batch-level fault tolerance

⸻

14. Key Design Principles

1. Hybrid Intelligence

LLM → feature extraction
Rules → decision

⸻

2. Explainability First

No black-box decisions.

⸻

3. Conservative Risk Bias

Minimize false approvals.

⸻

4. Separation of Concerns

Agents / Tools / Docs / Decision isolated.

⸻

5. Production Simulation

Includes:
• async execution
• evaluation
• structured logging

⸻

15. Known Limitations
    • Synthetic dataset
    • Limited document diversity
    • No real bureau APIs
    • No temporal credit history

⸻

16. Next Evolution
    • Replace rules → ML scoring layer
    • Add liabilities + EMI aggregation
    • Add vector DB (RAG for docs)
    • Add monitoring + tracing
    • Scale dataset (1000+)

⸻

17. System Classification

Type: Applied AI System
Category: Decision Intelligence (BFSI)
Level: Production-Grade Simulation

⸻

Final State

Not a demo.
A complete underwriting system simulation with:

- multi-agent orchestration
- document intelligence
- explainable decisions
- async execution
- evaluation pipeline
