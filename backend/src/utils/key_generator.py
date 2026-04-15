import secrets
from datetime import datetime, timedelta


def generate_activation_key(days_valid: int = 7) -> tuple[str, datetime]:
    """Генерирует ключ активации и дату истечения"""
    key = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=days_valid)
    return key, expires_at