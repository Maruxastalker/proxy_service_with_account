import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "proxy_service",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.tasks.email_tasks", "src.tasks.cleanup_tasks"]
)

celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    broker_transport_options={'visibility_timeout': 3600},
    task_always_eager=False,
    broker_connection_retry_on_startup=True,
    event_queue_prefix='celeryev',
    event_queue_ttl=5
)