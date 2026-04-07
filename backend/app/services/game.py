import importlib.util
import inspect
import logging
import sys
from pathlib import Path

from ..games import Game
from ..helpers.json_safe_value import _json_safe_value
from ..schemas.game import GameResponse
from ..state import state

logger = logging.getLogger(__name__)

# We cannot save this to App state since it contains literal games intances with code
games: dict[str, Game] = {} 


def _game_to_response(game: Game) -> GameResponse:
    return GameResponse.model_validate(game.model_dump(exclude={"default_game_data"}))

def discover_and_load_games() -> None:
    games_dir = Path("backend/app/games")
    games.clear()

    for file in games_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = file.stem
        game_key = module_name
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, file)
            if spec is None or spec.loader is None:
                logger.error("Failed to load %s: invalid module spec", file.name)
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            loaded_for_file = 0
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Game) and obj is not Game:
                    if loaded_for_file > 0:
                        logger.warning("Multiple game classes in %s, ignoring %s", file.name, name)
                        continue

                    game_instance = obj()
                    saved_game_state = state.data.games.get(game_key)
                    if saved_game_state is not None:
                        game_instance.apply_settings(saved_game_state.settings)

                    logger.info("Registered game: %s (%s)", name, game_key)
                    games[game_key] = game_instance
                    loaded_for_file += 1

            if loaded_for_file == 0:
                logger.warning("No Game subclass found in %s", file.name)
        except Exception as e:
            # One broken mod never crashes the app
            logger.error("Failed to load %s: %s", file.name, e, exc_info=True)

    if state.data.current_game is not None and state.data.current_game not in games:
        logger.warning("Current game '%s' is not available anymore, resetting", state.data.current_game)
        state.data.current_game = None

    persisted_games = {}
    for game_key, game_instance in games.items():
        persisted = game_instance.get_persisted_state()
        persisted_games[game_key] = persisted.model_copy(
            update={"settings": _json_safe_value(persisted.settings)}
        )

    state.data.games = persisted_games

    state.save()


def get_current_game() -> GameResponse | None:
    game_key = state.data.current_game
    if game_key is None:
        return None

    game = games.get(game_key)
    if game is None:
        logger.warning("Current game key '%s' is missing in loaded games", game_key)
        state.data.current_game = None
        state.save()
        return None

    return _game_to_response(game)


def list_games() -> list[GameResponse]:
    return [_game_to_response(game) for game in games.values()]


def set_current_game(game_key: str) -> GameResponse:
    if game_key not in games:
        raise ValueError(f"Game with key '{game_key}' does not exist")

    state.data.current_game = game_key
    state.save()

    return _game_to_response(games[game_key])


def start_game() -> None:
    # Placeholder for future game lifecycle logic.
    return None


def stop_game() -> None:
    # Placeholder for future game lifecycle logic.
    return None

