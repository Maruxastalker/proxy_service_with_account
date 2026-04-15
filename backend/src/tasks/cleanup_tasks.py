from celery import shared_task
from celery.schedules import crontab
from src.tasks.celery_app import celery_app
from datetime import datetime
from src.database import SessionLocal
from src.models.user import User
from src.models.virtual_machine import VirtualMachine


@shared_task
def cleanup_expired_keys():
    """Очистка просроченных ключей"""
    db = SessionLocal()
    try:
        db.query(User).filter(
            User.activation_key_expires < datetime.utcnow()
        ).update({"activation_key": None, "activation_key_expires": None})
        db.commit()
    finally:
        db.close()


@shared_task
def cleanup_stale_vm_connections(hours: int = 24):
    """Освободить VM, если last_used_at > hours"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        db.query(VirtualMachine).filter(
            VirtualMachine.last_used_at < cutoff,
            VirtualMachine.current_user_id.is_not(None)
        ).update({"current_user_id": None})
        db.commit()
    finally:
        db.close()


celery_app.conf.beat_schedule = {
    "cleanup-expired-keys": {
        "task": "src.tasks.cleanup_tasks.cleanup_expired_keys",
        "schedule": crontab(hour=0, minute=0),
    },
    "cleanup-stale-vms": {
        "task": "src.tasks.cleanup_tasks.cleanup_stale_vm_connections",
        "schedule": crontab(hour="*/6"),
    },
}