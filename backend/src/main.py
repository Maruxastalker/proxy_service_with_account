from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from src.config import settings
from src.api.routes import auth, users, activate, admin_vms
from src.websocket.manager import manager
from src.database import SessionLocal
from src.models.user import User
from src.models.virtual_machine import VirtualMachine
import asyncio

app = FastAPI(
    title=settings.app_name,
    description="Сервис прокси-доступа с регистрацией и личным кабинетом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(activate.router, prefix="/api/v1", tags=["Activation"])
app.include_router(admin_vms.router, prefix="/api/v1/admin/vms", tags=["Admin"])


async def verify_websocket_token(token: str):
    """Проверка JWT токена для WebSocket"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = int(payload.get("sub"))
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        return user
    except JWTError:
        return None


async def periodic_status_sender(user_id: int):
    """Периодическая отправка статуса пользователю"""
    while True:
        await asyncio.sleep(30)
        
        if user_id not in manager.active_connections:
            break
        
        db = SessionLocal()
        try:
            vm = db.query(VirtualMachine).filter(
                VirtualMachine.current_user_id == user_id
            ).first()
            
            if vm:
                await manager.send_status(
                    user_id, 
                    "connected",
                    vm_info={
                        "host": vm.host,
                        "port": vm.port,
                        "protocol": vm.protocol
                    }
                )
            else:
                current_status = manager.get_status(user_id)
                if current_status != "disconnected":
                    await manager.send_status(user_id, "disconnected")
        except Exception as e:
            print(f"Periodic status error for user {user_id}: {e}")
        finally:
            db.close()


@app.websocket("/ws/status/{user_id}")
async def websocket_status(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...)
):
    user = await verify_websocket_token(token)
    if not user or user.id != user_id:
        await websocket.close(code=1008)
        return
    
    await manager.connect(user_id, websocket)
    
    periodic_task = asyncio.create_task(periodic_status_sender(user_id))
    
    try:
        db = SessionLocal()
        try:
            vm = db.query(VirtualMachine).filter(
                VirtualMachine.current_user_id == user_id
            ).first()
            db.close()
            
            if vm:
                await manager.send_status(
                    user_id, 
                    "connected",
                    vm_info={
                        "host": vm.host,
                        "port": vm.port,
                        "protocol": vm.protocol
                    }
                )
            else:
                await manager.send_status(user_id, "disconnected")
        except:
            pass
        
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_message(user_id, {"type": "pong"})
            elif data == "status":
                current_status = manager.get_status(user_id)
                await manager.send_message(user_id, {
                    "type": "status_response",
                    "status": current_status or "unknown"
                })
                
    except WebSocketDisconnect:
        periodic_task.cancel()
        manager.disconnect(user_id)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}