from celery import Celery


celery_app = Celery(
    "service_desk_tasks",
    broker="redis://0.0.0.0:6379/0",
    backend="redis://0.0.0.0:6379/0",
)

celery_app.conf.update(
    result_backend="redis://127.0.0.1:6379/0",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)
