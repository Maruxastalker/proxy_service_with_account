from fastapi import WebSocket
from typing import Dict, Optional
from datetime import datetime
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_status: Dict[int, str] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_status[user_id] = "connected"
        print(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            self.user_status[user_id] = "disconnected"
            print(f"WebSocket disconnected for user {user_id}")
    
    async def send_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def send_status(self, user_id: int, status: str, vm_info: dict = None, error: str = None):
        """Отправка статуса пользователю"""
        message = {
            "type": "connection_status",
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        if vm_info:
            message["vm_info"] = vm_info
        if error:
            message["error"] = error
        
        self.user_status[user_id] = status
        await self.send_message(user_id, message)
    
    async def broadcast_to_all(self, message: dict):
        """Отправить сообщение всем подключенным пользователям"""
        for user_id in list(self.active_connections.keys()):
            await self.send_message(user_id, message)
    
    def get_status(self, user_id: int) -> Optional[str]:
        """Получить статус пользователя"""
        return self.user_status.get(user_id)


manager = ConnectionManager()