from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from src.models.user import User
from src.models.virtual_machine import VirtualMachine
from src.schemas.vm import VMCreate
from src.websocket.manager import manager
import asyncio


class VMService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_vms(self):
        return self.db.query(VirtualMachine).all()
    
    def create_vm(self, vm_data: VMCreate):
        vm = VirtualMachine(
            name=vm_data.name,
            host=vm_data.host,
            port=vm_data.port,
            protocol=vm_data.protocol
        )
        self.db.add(vm)
        self.db.commit()
        self.db.refresh(vm)
        return vm
    
    def delete_vm(self, vm_id: int):
        vm = self.db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if not vm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="VM not found"
            )
        self.db.delete(vm)
        self.db.commit()
    
    def activate_key(self, user: User, activation_key: str):
        
        if user.activation_key != activation_key:
            asyncio.create_task(manager.send_status(
                user.id, 
                "error", 
                error="Invalid activation key"
            ))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid activation key"
            )
        
        if user.activation_key_expires and user.activation_key_expires < datetime.utcnow():
            asyncio.create_task(manager.send_status(
                user.id, 
                "error", 
                error="Activation key expired"
            ))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Activation key expired"
            )
        
        free_vm = self.db.query(VirtualMachine).filter(
            VirtualMachine.current_user_id.is_(None),
            VirtualMachine.is_active == True
        ).first()
        
        if not free_vm:
            asyncio.create_task(manager.send_status(
                user.id, 
                "no_free_vms",
                error="All proxy servers are busy"
            ))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No free proxy servers available"
            )
        
        free_vm.current_user_id = user.id
        free_vm.last_used_at = datetime.utcnow()
        self.db.commit()
        
        asyncio.create_task(manager.send_status(
            user.id, 
            "connected",
            vm_info={
                "host": free_vm.host,
                "port": free_vm.port,
                "protocol": free_vm.protocol,
                "vm_id": free_vm.id,
                "vm_name": free_vm.name
            }
        ))
        
        return {
            "host": free_vm.host,
            "port": free_vm.port,
            "protocol": free_vm.protocol,
            "message": "Successfully connected to proxy server"
        }
    
    def disconnect_user(self, user_id: int):
        vm = self.db.query(VirtualMachine).filter(
            VirtualMachine.current_user_id == user_id
        ).first()
        
        if vm:
            vm.current_user_id = None
            self.db.commit()
            
            asyncio.create_task(manager.send_status(
                user_id, 
                "disconnected"
            ))
        
        return vm
    
    def get_user_vm(self, user_id: int):
        """Получить VM, к которой подключен пользователь"""
        return self.db.query(VirtualMachine).filter(
            VirtualMachine.current_user_id == user_id
        ).first()