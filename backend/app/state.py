# app/state.py
import json
import logging
from pathlib import Path
from typing import Any
from pydantic import Field

from .schemas.base import BaseSchema

logger = logging.getLogger(__name__)
DATA_PATH = Path("./SLData.json")

class AppData(BaseSchema):
    pass


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
        with open(self._path, "r", encoding="utf-8") as f:
            return AppData.model_validate(json.load(f))

    def save(self) -> None:
        payload = self.data.model_dump(by_alias=False)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info("State saved to %s", self._path)

    def reload(self) -> None:
        self.data = self._load()
        logger.debug("State reloaded from %s", self._path)

state = StateManager()