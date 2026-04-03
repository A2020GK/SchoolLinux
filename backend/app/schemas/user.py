from . import BaseSchema
from .game import GameTask

class UserResponse(BaseSchema):
    ip: str
    pc_name: str
    score: int
    
class User(UserResponse):
    task: GameTask | None = None