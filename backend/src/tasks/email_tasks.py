from celery import shared_task
from src.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from celery.signals import worker_ready
from src.tasks.celery_app import celery_app

@worker_ready.connect
def at_worker_ready(sender, **k):
    print("Celery worker is ready!")
    print(f"Broker URL: {sender.app.conf.broker_url}")

@celery_app.task
def send_activation_email(email_to: str, activation_key: str):
    """Отправка письма с ключом активации"""
    try:
        message = MIMEMultipart()
        message["From"] = settings.smtp_from_email
        message["To"] = email_to
        message["Subject"] = "Your Activation Key"
        
        body = f"""
        Hello!
        
        Your activation key is: {activation_key}
        
        This key will expire in 7 days.
        
        Use this key in the desktop application to connect to the proxy server.
        
        Best regards,
        Proxy Service Team
        """
        
        message.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_port == 587:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        
        return {"success": True, "message": "Email sent"}
    except Exception as e:
        return {"success": False, "error": str(e)}