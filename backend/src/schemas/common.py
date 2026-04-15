from pydantic import BaseModel
from typing import Any, Optional


class MessageResponse(BaseModel):
    message: str
    details: Optional[Any] = None