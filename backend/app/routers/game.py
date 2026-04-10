from fastapi import APIRouter, HTTPException, Body
from ..services.game import get_current_game_response as get_current_game_service
from ..services.game import list_games as list_games_service
from ..services.game import set_current_game as set_current_game_service
from ..services.game import start_game as start_game_service
from ..services.game import stop_game as stop_game_service
from ..services.game import check as check_service
from ..schemas.game import GameResponse, GameChangeRequest, GameResponseSafe
from backend.app.socket import manager
from typing import Annotated
from backend.app.dependencies.user import TeacherOnlyDep, IsTeacherDep, IpDep

router = APIRouter(prefix="/game", tags=["Game"])


@router.get("/")
async def get_current_game(teacher: IsTeacherDep) -> GameResponseSafe | GameResponse | None:
    """Get the currently selected game."""
    return get_current_game_service(safe=not teacher)

@router.get("/list")
async def list_games(_: TeacherOnlyDep) -> dict[str, GameResponse]:
    """List all available games."""
    return list_games_service()
    
@router.post("/")
async def set_current_game(game_change_request: GameChangeRequest, _: TeacherOnlyDep) -> GameResponse:
    """Set the current game by key."""
    try:
        new = set_current_game_service(**game_change_request.model_dump())
        await manager.send_to_everyone_except_teacher("game_change", new.model_dump(exclude={"settings_form", "anticheat_required"}))
        return new
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.post("/check")
async def check(ip: IpDep, submission: Annotated[str, Body()] = ""):
    """Check a string submission for the current game and return score delta."""
    current_game = get_current_game_service()
    if current_game is None:
        raise HTTPException(status_code=404, detail="No game is currently selected")
    if not current_game.string_submission:
        raise HTTPException(status_code=400, detail="Current game does not accept string submissions")
    
    score = check_service()
   

@router.post("/start")
async def start(_: TeacherOnlyDep):
    return start_game_service()

@router.post("/stop")
async def stop(_: TeacherOnlyDep):
    return stop_game_service()