from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.api.dependencies import get_current_user
from src.models.user import User
from src.schemas.vm import VMActivateRequest, VMActivateResponse
from src.services.vm_service import VMService

router = APIRouter()


@router.post("/activate", response_model=VMActivateResponse)
async def activate_key(
    request: VMActivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vm_service = VMService(db)
    return vm_service.activate_key(current_user, request.activation_key)

@router.post("/disconnect")
async def disconnect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отключить пользователя от VM"""
    vm_service = VMService(db)
    vm_service.disconnect_user(current_user.id)
    return {"message": "Disconnected from proxy"}