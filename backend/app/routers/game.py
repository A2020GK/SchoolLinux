from fastapi import APIRouter, HTTPException
from ..services.game import get_current_game as get_current_game_service
from ..services.game import list_games as list_games_service
from ..services.game import set_current_game as set_current_game_service
from ..services.game import start_game as start_game_service
from ..services.game import stop_game as stop_game_service
from ..schemas.game import GameResponse
from backend.app.dependencies.user import TeacherOnlyDep

router = APIRouter(prefix="/game", tags=["Game"])


@router.get("/current")
async def get_current_game() -> GameResponse | None:
    """Get the currently selected game."""
    return get_current_game_service()

@router.get("/list")
async def list_games(_: TeacherOnlyDep) -> list[GameResponse]:
    """List all available games."""
    return list_games_service()
    
@router.post("/set/{game_key}")
async def set_current_game(game_key: str, _: TeacherOnlyDep) -> GameResponse:
    """Set the current game by key."""
    try:
        return set_current_game_service(game_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.post("/start")
async def start(_: TeacherOnlyDep):
    return start_game_service()

@router.post("/stop")
async def stop(_: TeacherOnlyDep):
    return stop_game_service()