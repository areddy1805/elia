from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import time
import uuid

from app.supervisor.supervisor import LoanSupervisor
from app.core.logger import log_event
from app.db.database import Database

from app.queue.tasks import process_loan
from app.queue.celery_app import celery_app

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware


# ------------------------
# INIT
# ------------------------
app = FastAPI()
supervisor = LoanSupervisor()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


def get_db():
    return Database()


# ------------------------
# STRICT SCHEMA
# ------------------------
class Applicant(BaseModel):
    name: str
    age: int


class Employment(BaseModel):
    type: str
    monthly_income: float


class Loan(BaseModel):
    amount: float
    tenure_months: int


class Application(BaseModel):
    application_id: str
    applicant: Applicant
    employment: Employment
    loan: Loan


class LoanRequest(BaseModel):
    application: Application


# ------------------------
# SYNC ENDPOINT
# ------------------------
@app.post("/evaluate-loan")
def evaluate_loan(req: LoanRequest):

    start = time.time()
    application = req.application.dict()

    log_event("request_received", {
        "application_id": application["application_id"]
    })

    try:
        state = supervisor.run(application)
    except Exception as e:
        log_event("error", str(e))
        return {"error": "internal_failure"}

    latency = round(time.time() - start, 3)

    log_event("decision_made", {
        "application_id": state.application_id,
        "decision": state.decision,
        "confidence": getattr(state, "confidence", None),
        "latency": latency
    })

    db = get_db()
    db.insert_decision(state, latency)

    return {
        "application_id": state.application_id,
        "decision": state.decision,
        "reason": state.reason,
        "confidence": getattr(state, "confidence", None),
        "latency_sec": latency
    }


# ------------------------
# ASYNC ENDPOINT
# ------------------------
@app.post("/evaluate-loan-async")
@limiter.limit("10/minute")
def evaluate_loan_async(request: Request, req: LoanRequest):

    application = req.application.dict()
    request_id = str(uuid.uuid4())

    log_event("async_request_received", {
        "request_id": request_id,
        "application_id": application["application_id"]
    })

    task = process_loan.delay(application)

    return {
        "request_id": request_id,
        "task_id": task.id,
        "status": "processing"
    }


# ------------------------
# RESULT ENDPOINT
# ------------------------
@app.get("/result/{task_id}")
def get_result(task_id: str):

    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return {"status": "pending"}

    if task.state == "SUCCESS":
        return {
            "status": "completed",
            "result": task.result
        }

    if task.state == "FAILURE":
        return {
            "status": "failed",
            "error": str(task.result)
        }

    return {"status": task.state}


# ------------------------
# DECISION HISTORY
# ------------------------
@app.get("/decisions")
def get_decisions():

    db = get_db()
    cursor = db.conn.execute(
        "SELECT * FROM decisions ORDER BY id DESC LIMIT 10"
    )
    rows = cursor.fetchall()

    return [
        {
            "application_id": r[1],
            "decision": r[2],
            "confidence": r[3],
            "latency": r[4],
            "timestamp": r[5]
        }
        for r in rows
    ]


# ------------------------
# METRICS
# ------------------------
@app.get("/metrics")
def metrics():

    db = get_db()
    cursor = db.conn.execute("SELECT COUNT(*) FROM decisions")
    total = cursor.fetchone()[0]

    return {
        "total_requests": total
    }


# ------------------------
# HEALTH
# ------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=True)