from fastapi import APIRouter
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

    game = state.data.games.get(game_key)
    if game is None:
        logger.warning("Current game key '%s' is missing in loaded games", game_key)
        return None

    return GameResponse.model_validate(game.model_dump(exclude={"default_game_data", "game_data"}))

@router.get("/list")
async def list_games() -> list[GameResponse]:
    """List all available games."""
    return [
        GameResponse.model_validate(game.model_dump(exclude={"default_game_data", "game_data"}))
        for game in games.values()
    ]