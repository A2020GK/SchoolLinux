from .base import BaseSchema
from typing import Any

class RegisterRequest(BaseSchema):
    name: str
    pc_name: str

class UserResponse(BaseSchema):
    ip: str
    score: int = 0
    kicked: bool = False
    
class User(UserResponse):
    game_data: dict[Any, Any] = {}

