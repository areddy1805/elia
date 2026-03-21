import time

from app.queue.celery_app import celery_app
from app.supervisor.supervisor import LoanSupervisor
from app.db.database import Database
from app.core.logger import log_event


supervisor = LoanSupervisor()
db = Database()


@celery_app.task(name="app.queue.tasks.process_loan")
def process_loan(application):

    start = time.time()

    log_event("worker_started", application)

    state = supervisor.run(application)

    latency = round(time.time() - start, 3)

    db.insert_decision(state, latency)

    log_event("worker_completed", {
        "application_id": state.application_id,
        "decision": state.decision,
        "latency": latency
    })

    return {
        "application_id": state.application_id,
        "decision": state.decision,
        "latency": latency
    }