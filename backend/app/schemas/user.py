from .base import BaseSchema
from typing import Any

class RegisterRequest(BaseSchema):
    name: str
    pc_name: str

class SafeUserData(RegisterRequest):
    score: int = 0
    kicked: bool = False

class User(SafeUserData):
    game_data: dict[Any, Any] = {}

class UserResponse(BaseSchema):
    """Response returned to any client. is_teacher indicates whether the caller is a teacher.
    user contains the caller's SafeUserData when is_teacher is False, and is None when is_teacher is True."""
    is_teacher: bool
    user: SafeUserData | None

