from fastapi import APIRouter, Body, HTTPException, Request
from typing import Annotated
from backend.app.schemas.user import RegisterRequest, UserResponse, SafeUserData
from backend.app.dependencies.user import TeacherOnlyDep, CurrentUserDep, IpDep, IsTeacherDep
from backend.app.services.user import register_user, get_all_users as get_all_users_service, set_kicked
from backend.app.socket.manager import manager

router = APIRouter(prefix="/user", tags=["User"])

convert_to_safe = lambda user: SafeUserData(ip=user.ip, score=user.score, kicked=user.kicked)
convert_to_safe_list = lambda users: [convert_to_safe(user) for user in users]

@router.post("/register")
async def register(regrequest: RegisterRequest, ip: IpDep, is_teacher: IsTeacherDep) -> UserResponse:
    """Register a new user based on their IP address. Teachers (localhost) are identified and returned with is_teacher=True and no user data."""
    if is_teacher:
        return UserResponse(is_teacher=True, user=None)

    user, created = register_user(regrequest, ip=ip)

    if created:
        await manager.send_to_teacher("users_update", [i.model_dump() for i in convert_to_safe_list(get_all_users_service())])

    return UserResponse(is_teacher=False, user=convert_to_safe(user))

@router.get("/all")
async def get_all_users(_: TeacherOnlyDep) -> list[SafeUserData]:
    """Get a list of all registered users. Only for teachers (localhost)."""
    return convert_to_safe_list(get_all_users_service())

@router.get("/me")
async def get_current_user(user: CurrentUserDep, is_teacher: IsTeacherDep) -> UserResponse:
    """Get the current user's information based on their IP address."""
    if is_teacher:
        return UserResponse(is_teacher=True, user=None)
    return UserResponse(is_teacher=False, user=convert_to_safe(user))

@router.post("/kick/{ip}")
async def kick_user(ip: str, kicked: Annotated[bool, Body()], _: TeacherOnlyDep):
    """Kick a user by their IP address. Only for teachers (localhost)."""
    success = set_kicked(ip, kicked)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")
    await manager.send_to_ip(ip, "kicked", {"kicked": kicked})
    return success