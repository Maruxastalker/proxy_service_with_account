from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.api.dependencies import get_current_user
from src.models.user import User
from src.schemas.user import UserResponse, PasswordChange, KeyResponse
from src.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user_service.change_password(current_user, password_data.old_password, password_data.new_password)
    return {"message": "Password changed successfully"}


@router.post("/renew-key", response_model=KeyResponse)
async def renew_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.renew_activation_key(current_user)


@router.get("/my-key", response_model=KeyResponse)
async def get_my_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.get_activation_key(current_user)