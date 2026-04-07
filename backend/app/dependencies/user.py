from backend.app.services.user import get_user_by_ip, is_teacher as is_teacher_act
from fastapi import Request, Depends, HTTPException
from typing import Annotated
from backend.app.schemas.user import User
from backend.app.config import config


def _get_request_ip(request: Request) -> str:
    """Resolve client IP with optional debug override for local development."""
    if config.allow_ip_override:
        debug_ip = request.headers.get(config.ip_override_header)
        if debug_ip:
            return debug_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"
IpDep = Annotated[str, Depends(_get_request_ip)]

def get_current_user(request: Request, ip: IpDep) -> User | None:
    """FastAPI Dependency to get the current user based on the client's IP address."""
    return get_user_by_ip(ip)

def is_teacher(request: Request, ip: IpDep):
    """FastAPI Dependency to check if the current user is a teacher."""
    return is_teacher_act(ip)

def teacher_only(is_teacher: bool = Depends(is_teacher)):
    """FastAPI Dependency to restrict access to teachers only."""
    if not is_teacher:
        raise HTTPException(status_code=403, detail="Access forbidden: Teachers only.")

CurrentUserDep = Annotated[User, Depends(get_current_user)]
IsTeacherDep = Annotated[bool, Depends(is_teacher)]
TeacherOnlyDep = Annotated[None, Depends(teacher_only)]