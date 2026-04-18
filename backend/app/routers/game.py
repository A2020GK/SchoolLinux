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
from ..services.user import get_all_users
from ..schemas.user import SafeUserData

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
    """Set the current game by key. Cannot change game when a game is running."""
    from ..state import state
    if state.data.state == "running":
        raise HTTPException(status_code=409, detail="Cannot change game while a game is running. Stop the game first.")
    try:
        new = set_current_game_service(**game_change_request.model_dump())
        await manager.send_to_everyone_except_teacher(
            "game_change",
            new.model_dump(by_alias=True, exclude={"settings_form", "anticheat_required"}),
        )
        return new
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.post("/check")
async def check(ip: IpDep, submission: Annotated[str, Body()] = ""):
    """Run game check for the current user and return updated score.
    For string-based games submission is used, otherwise backend SSH check is executed."""
    from ..services.user import get_all_users
    from ..schemas.user import SafeUserData
    
    convert_to_safe = lambda user: SafeUserData(score=user.score, kicked=user.kicked, name=user.name, pc_name=user.pc_name)
    convert_to_safe_dict = lambda users: {item_ip: convert_to_safe(item_user) for item_ip, item_user in users.items()}
    
    current_game = get_current_game_service()
    if current_game is None:
        raise HTTPException(status_code=404, detail="No game is currently selected")
    
    users = get_all_users()
    user = users.get(ip)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.kicked:
        raise HTTPException(status_code=403, detail="Cannot check for kicked users")

    score_before = user.score
    score = check_service(ip, submission if current_game.string_submission else "")

    if score != score_before:
        await manager.send_to_teacher(
            "users_update",
            {item_ip: item.model_dump(by_alias=True) for item_ip, item in convert_to_safe_dict(get_all_users()).items()},
        )

    return score

@router.post("/start")
async def start(_: TeacherOnlyDep):
    """Start the current game with state transition idle -> init -> running."""
    from ..state import state
    if state.data.state != "idle":
        raise HTTPException(status_code=409, detail=f"Cannot start game when state is '{state.data.state}'. Only idle games can be started.")

    current_game = get_current_game_service()
    if current_game is None:
        raise HTTPException(status_code=404, detail="No game is currently selected")

    state.data.state = "init"
    state.save()
    await manager.send_to_everyone("game_state_changed", {"state": state.data.state})

    try:
        result = start_game_service()
    except ValueError as exc:
        state.data.state = "idle"
        state.save()
        await manager.send_to_everyone("game_state_changed", {"state": state.data.state})
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        state.data.state = "idle"
        state.save()
        await manager.send_to_everyone("game_state_changed", {"state": state.data.state})
        raise HTTPException(status_code=500, detail="Failed to start game") from exc

    state.data.state = "running"
    state.save()
    await manager.send_to_everyone("game_state_changed", {"state": state.data.state})

    await manager.send_to_teacher(
        "users_update",
        {
            item_ip: SafeUserData(
                score=item_user.score,
                kicked=item_user.kicked,
                name=item_user.name,
                pc_name=item_user.pc_name,
            ).model_dump(by_alias=True)
            for item_ip, item_user in get_all_users().items()
        },
    )

    for item_ip, item_user in get_all_users().items():
        await manager.send_to_ip(
            item_ip,
            "user_update",
            SafeUserData(
                score=item_user.score,
                kicked=item_user.kicked,
                name=item_user.name,
                pc_name=item_user.pc_name,
            ).model_dump(by_alias=True),
        )

    return result

@router.post("/stop")
async def stop(_: TeacherOnlyDep):
    """Stop the current game. Sets system state to 'idle'."""
    from ..state import state
    if state.data.state != "running":
        raise HTTPException(status_code=409, detail=f"Cannot stop game when state is '{state.data.state}'. Only running games can be interrupted.")

    try:
        result = stop_game_service()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    state.data.state = "idle"
    state.save()
    await manager.send_to_everyone("game_state_changed", {"state": state.data.state})
    return result

@router.get("/state")
async def get_game_state() -> dict:
    """Get the current game system state."""
    from ..state import state
    return {"state": state.data.state}