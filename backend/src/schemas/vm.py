from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ProtocolEnum(str, Enum):
    SOCKS5 = "socks5"
    HTTP = "http"
    HTTPS = "https"


class VMResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    protocol: ProtocolEnum
    is_active: bool
    current_user_id: Optional[int]
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VMCreate(BaseModel):
    name: str
    host: str
    port: int
    protocol: ProtocolEnum


class VMActivateRequest(BaseModel):
    activation_key: str


class VMActivateResponse(BaseModel):
    host: str
    port: int
    protocol: ProtocolEnum
    message: str