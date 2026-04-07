# app/state.py
import json
import logging
import re
from pathlib import Path
from typing import Any
from pydantic import Field, model_validator

from .schemas.base import BaseSchema
from .schemas.game import GamePersistedState

logger = logging.getLogger(__name__)
DATA_PATH = Path("./SLData.json")
JSON_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _is_valid_game_key(value: str) -> bool:
    return bool(JSON_KEY_PATTERN.fullmatch(value))

class AppData(BaseSchema):
    current_game: str | None = None
    games: dict[str, GamePersistedState] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_games_payload(self) -> "AppData":
        invalid_keys = [key for key in self.games if not _is_valid_game_key(key)]
        if invalid_keys:
            invalid = ", ".join(sorted(invalid_keys))
            raise ValueError(f"Invalid game key(s): {invalid}")

        if self.current_game is not None and self.current_game not in self.games:
            raise ValueError("current_game must match one of loaded game keys")

        return self


class StateManager:
    """Typed JSON-backed state manager."""
    def __init__(self, path: Path = DATA_PATH):
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
        self.save()  # Ensure file exists

    def _load(self) -> AppData:
        if not self._path.exists():
            return AppData()

        try:
            with open(self._path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except json.JSONDecodeError as exc:
            logger.warning("State file is not valid JSON, resetting in-memory state: %s", exc)
            return AppData()

        try:
            return AppData.model_validate(payload)
        except Exception as exc:
            logger.warning("Invalid state payload, trying to sanitize: %s", exc)

        raw_games = payload.get("games") if isinstance(payload, dict) else None
        sanitized_games: dict[str, GamePersistedState] = {}
        if isinstance(raw_games, dict):
            for key, game_payload in raw_games.items():
                if not isinstance(key, str) or not _is_valid_game_key(key):
                    logger.warning("Skipping invalid game key in state: %r", key)
                    continue
                try:
                    sanitized_games[key] = GamePersistedState.model_validate(game_payload)
                except Exception as exc:
                    logger.warning("Skipping invalid game payload for '%s': %s", key, exc)

        raw_current = None
        if isinstance(payload, dict):
            raw_current = payload.get("currentGame", payload.get("current_game"))
        current_game = raw_current if isinstance(raw_current, str) and raw_current in sanitized_games else None

        return AppData(games=sanitized_games, current_game=current_game)

    def save(self) -> None:
        payload = self.data.model_dump(by_alias=True, mode="json")
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info("State saved to %s", self._path)

    def reload(self) -> None:
        self.data = self._load()
        logger.debug("State reloaded from %s", self._path)

state = StateManager()