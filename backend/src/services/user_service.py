from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from src.models.user import User
from src.services.auth_service import AuthService
from src.utils.key_generator import generate_activation_key
from src.tasks.email_tasks import send_activation_email
import secrets


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)
    
    def change_password(self, user: User, old_password: str, new_password: str):
        if not self.auth_service.verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        user.password_hash = self.auth_service.hash_password(new_password)
        self.db.commit()
    
    def generate_activation_key(self) -> tuple[str, datetime]:
        return generate_activation_key(days_valid=7)
    
    def renew_activation_key(self, user: User):
        key, expires_at = self.generate_activation_key()
        user.activation_key = key
        user.activation_key_expires = expires_at
        self.db.commit()
        
        send_activation_email.delay(user.email, key)
        
        return {
            "activation_key": key,
            "expires_at": expires_at
        }
    
    def get_activation_key(self, user: User):
        if not user.activation_key:
            return self.renew_activation_key(user)
        
        if user.activation_key_expires and user.activation_key_expires < datetime.utcnow():
            return self.renew_activation_key(user)
        
        return {
            "activation_key": user.activation_key,
            "expires_at": user.activation_key_expires
        }