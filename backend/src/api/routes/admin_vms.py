from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.schemas.vm import VMResponse, VMCreate
from src.services.vm_service import VMService

router = APIRouter()


@router.get("/", response_model=List[VMResponse])
async def list_vms(db: Session = Depends(get_db)):
    vm_service = VMService(db)
    return vm_service.get_all_vms()


@router.post("/", response_model=VMResponse, status_code=status.HTTP_201_CREATED)
async def create_vm(vm_data: VMCreate, db: Session = Depends(get_db)):
    vm_service = VMService(db)
    return vm_service.create_vm(vm_data)


@router.delete("/{vm_id}")
async def delete_vm(vm_id: int, db: Session = Depends(get_db)):
    vm_service = VMService(db)
    vm_service.delete_vm(vm_id)
    return {"message": "VM deleted successfully"}