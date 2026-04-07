from fastapi import APIRouter, Body, HTTPException, Request
from typing import Annotated
from backend.app.schemas.user import RegisterRequest, UserResponse
from backend.app.dependencies.user import TeacherOnlyDep, CurrentUserDep, IpDep
from backend.app.services.user import register_user, get_all_users as get_all_users_service, set_kicked
from backend.app.socket.manager import manager

router = APIRouter(prefix="/user", tags=["User"])

convert_to_response = lambda user: UserResponse(ip=user.ip, score=user.score, kicked=user.kicked)
convert_to_response_list = lambda users: [convert_to_response(user) for user in users]

@router.post("/register")
async def register(regrequest: RegisterRequest, ip: IpDep ) -> UserResponse | None:
    """Register a new user based on their IP address. If the user is a teacher (localhost), registration is not allowed."""
    user, created = register_user(regrequest, ip=ip)
    
    if created:
        await manager.send_to_teacher("users_update", [i.model_dump() for i in convert_to_response_list(get_all_users_service())])
    
    return user

@router.get("/all")
async def get_all_users(_: TeacherOnlyDep) -> list[UserResponse]:
    """Get a list of all registered users. Only for teachers (localhost)."""
    return convert_to_response_list(get_all_users_service())

@router.get("/me")
async def get_current_user(user: CurrentUserDep) -> UserResponse:
    """Get the current user's information based on their IP address."""
    return convert_to_response(user)

@router.post("/kick/{ip}")
async def kick_user(ip: str, kicked: Annotated[bool, Body()], _: TeacherOnlyDep):
    """Kick a user by their IP address. Only for teachers (localhost)."""
    success = set_kicked(ip, kicked)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")
    await manager.send_to_ip(ip, "kicked", {"kicked": kicked})
    return success