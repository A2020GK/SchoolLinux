import importlib.util
import inspect
import logging
import sys
from pathlib import Path

from ..games import Game
from ..helpers.json_safe_value import _json_safe_value
from ..schemas.game import GameResponse, GameResponseSafe
from ..state import state
from .user import get_all_users
from backend.app.services.ssh import create_client_from_config

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


def get_current_game() -> Game | None:
    game_key = state.data.current_game
    if game_key is None:
        return None
    return games.get(game_key)

def get_current_game_response(safe: bool = False) -> GameResponse | None:
    game = get_current_game()
    if game is None:
        return None
    if safe:
        return GameResponseSafe.model_validate(_game_to_response(game).model_dump(exclude={"settings_form", "anticheat_required"}))
    return _game_to_response(game)


def list_games() -> dict[str, GameResponse]:
    return {game_key: _game_to_response(game) for game_key, game in games.items()}


def set_current_game(game_key: str, settings: dict[str, str | int | bool] | None) -> GameResponse:
    if game_key not in games:
        raise ValueError(f"Game with key '{game_key}' does not exist")

    state.data.current_game = game_key

    game = games[game_key]
    if settings is not None:
        game.apply_settings(settings)

    persisted = game.get_persisted_state()
    state.data.games[game_key] = persisted.model_copy(
        update={"settings": _json_safe_value(persisted.settings)}
    )

    state.save()
    return _game_to_response(game)


def start_game() -> None:
    # Placeholder for future game lifecycle logic.
    # Steps:
    # 1. Get current game
    # 2. Set system state to "init"
    # 3. Init game data for all user with game.default_game_data
    # 4. Call game.install for all users
    # 5. Set system state to "run"
    current_game = get_current_game()
    for ip, user in get_all_users().items():
        user.game_data = current_game.new_game_data()
        
        try:
            logger.info("Installing game for user %s (%s)", user.name, ip)
            client = create_client_from_config(ip)
            current_game.install(client, user.game_data)
            
        except Exception as exc:
            logger.error("Failed to install game for user %s (%s): %s", user.name, ip, exc, exc_info=True)
        
    state.save()

def stop_game() -> None:
    current_game = get_current_game()
    for ip, user in get_all_users().items():
        try:
            logger.info("Uninstalling game for user %s (%s)", user.name, ip)
            client = create_client_from_config(ip)
            current_game.uninstall(client, user.game_data)
            
        except Exception as exc:
            logger.error("Failed to uninstall game for user %s (%s): %s", user.name, ip, exc, exc_info=True)
    state.save()
    
def check(ip, submission: str = "") -> int:
    current_game = get_current_game()
    user = get_all_users().get(ip)
    if user is None:
        logger.warning("Check called for unknown user with IP %s", ip)
        return 0
    
    try:
        client = create_client_from_config(ip)
        if current_game.string_submission:
            user.score += current_game.check_string_submission(submission, user.game_data)
        else:
            user.score = current_game.check(client, user.game_data)

        logger.info("Checked game for user %s (%s), new score: %d", user.name, ip, user.score)
        state.save()
        return user.score
    except Exception as exc:
        logger.error("Failed to check game for user %s (%s): %s", user.name, ip, exc, exc_info=True)