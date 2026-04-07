from .base import BaseSchema
from typing import Any

class UserResponse(BaseSchema):
    ip: str
    pc_name: str
    score: int = 0
    
class User(UserResponse):
    game_data: dict[Any, Any] = {}

