from fastapi import APIRouter, HTTPException
from ..state import state
from ..services.game import games
from ..schemas.game import GameResponse
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter(prefix="/game", tags=["Game"])


@router.get("/current")
async def get_current_game() -> GameResponse | None:
    """Get the currently selected game."""
    game_key = state.data.current_game
    if game_key is None:
        return None

    game = games.get(game_key)
    if game is None:
        logger.warning("Current game key '%s' is missing in loaded games", game_key)
        return None

    return GameResponse.model_validate(game.model_dump(exclude={"default_game_data"}))

@router.get("/list")
async def list_games() -> list[GameResponse]:
    """List all available games."""
    return [
        GameResponse.model_validate(game.model_dump(exclude={"default_game_data"}))
        for game in games.values()
    ]
    
@router.post("/set/{game_key}")
async def set_current_game(game_key: str) -> GameResponse:
    """Set the current game by key."""
    if game_key not in games:
        raise HTTPException(status_code=404, detail=f"Game with key '{game_key}' does not exist")

    state.data.current_game = game_key
    state.save()

    game = games[game_key]
    return GameResponse.model_validate(game.model_dump(exclude={"default_game_data"}))

@router.post("/start")
async def start():
    # TODO: Implement game start logic, e.g. resetting game data, notifying clients, etc.
    pass

@router.post("/stop")
async def stop():
    # TODO: Implement game stop logic, e.g. cleaning up game data, notifying clients, etc.
    pass