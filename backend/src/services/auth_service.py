from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from src.models.user import User
from src.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def register(self, email: str, password: str):
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        from src.utils.key_generator import generate_activation_key
        key, expires_at = generate_activation_key(days_valid=7)
        
        user = User(
            email=email,
            password_hash=self.hash_password(password),
            is_active=True,
            activation_key=key,
            activation_key_expires=expires_at
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Отправляем письмо с ключом
        from src.tasks.email_tasks import send_activation_email
        send_activation_email.delay(email, key)
        
        access_token = self.create_access_token(user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    
    def login(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )
        
        access_token = self.create_access_token(user.id)
        return {"access_token": access_token, "token_type": "bearer"}