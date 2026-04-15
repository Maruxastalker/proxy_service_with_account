from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class ProtocolEnum(str, enum.Enum):
    SOCKS5 = "socks5"
    HTTP = "http"
    HTTPS = "https"


class VirtualMachine(Base):
    __tablename__ = "virtual_machines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(Enum(ProtocolEnum), nullable=False)
    is_active = Column(Boolean, default=True)
    current_user_id = Column(Integer, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)