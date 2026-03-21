from celery import Celery

celery_app = Celery(
    "elia",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# CRITICAL
celery_app.autodiscover_tasks(["app.queue"])