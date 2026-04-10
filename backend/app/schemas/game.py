from copy import deepcopy
from typing import Any, Literal, Optional

from pydantic import Field

from .base import BaseSchema


class GameSettingsItem(BaseSchema):
    """Represents one setting shown when configuring a game."""

    name: str
    type: Literal["string", "number", "boolean", "option"] = Field(..., description="Type of the setting value")
    options: dict[str, str] | None = Field(None, description="List of options for 'option' type settings")
    default: str | int | bool = Field(..., description="Default value of the setting")
    value: str | int | bool | None = Field(None, description="Actual value of the setting in this game instance")

    def normalize_value(self, raw_value: Any) -> str | int | bool:
        """Normalize raw input to the declared setting type."""
        if self.type == "number":
            return int(raw_value)

        if self.type == "boolean":
            if isinstance(raw_value, bool):
                return raw_value
            if isinstance(raw_value, str):
                lowered = raw_value.strip().lower()
                if lowered in {"true", "1", "yes", "on"}:
                    return True
                if lowered in {"false", "0", "no", "off"}:
                    return False
            return bool(raw_value)

        value = str(raw_value)
        if self.type == "option" and self.options is not None and value not in self.options:
            raise ValueError(f"Unsupported option '{value}'")
        return value


class GameResponseSafe(BaseSchema):
    name: str = "Base Game"
    description: str = "Base game description"
    
    string_submission: bool = False
    required_user_score: int = 0
    
    settings: dict[str, str | int | bool] = Field(default_factory=dict)
    
class GameResponse(GameResponseSafe):
    anticheat_required: bool = False
    settings_form: Optional[dict[str, GameSettingsItem]] = Field(default_factory=dict)
   

class GameChangeRequest(BaseSchema):
    game_key: str
    settings: Optional[dict[str, str | int | bool]] = None


class GamePersistedState(BaseSchema):
    """Minimal game state persisted to SLData.json."""

    settings: dict[str, str | int | bool] = Field(default_factory=dict)


class GameBase(GameResponse):
    """Utility base model shared by game implementations."""

    default_game_data: dict = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        """Create instance-local settings and initialize them from defaults."""
        self.settings_form = {
            key: item.model_copy(deep=True)
            for key, item in self.settings_form.items()
        }
        self.apply_settings(self.settings if self.settings else None)

    def apply_settings(self, settings: dict[str, Any] | None = None) -> None:
        """Apply setting values and keep settings form values in sync."""
        incoming = settings or {}
        applied: dict[str, str | int | bool] = {}

        for key, item in self.settings_form.items():
            value = incoming.get(key, item.default)
            item.value = item.normalize_value(value)
            applied[key] = item.value if item.value is not None else item.default

        self.settings = applied

    def get_persisted_state(self) -> GamePersistedState:
        """Return minimal persisted state for this game instance."""
        return GamePersistedState(
            settings=self.settings,
        )

    def new_game_data(self) -> dict[str, Any]:
        """Create a fresh runtime game data object for a new game start."""
        return deepcopy(self.default_game_data)