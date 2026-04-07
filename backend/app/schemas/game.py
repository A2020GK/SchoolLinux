from copy import deepcopy
from typing import Any, Literal

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


class GameResponse(BaseSchema):
    """Public representation of a game without runtime-only data."""

    name: str = "Base Game"
    description: str = "Base game description"

    string_submission: bool = False
    anticheat_required: bool = False

    required_user_score: int = 0
    settings_form: dict[str, GameSettingsItem] = Field(default_factory=dict)
    settings: dict[str, str | int | bool] = Field(default_factory=dict)


class GamePersistedState(BaseSchema):
    """Minimal game state persisted to SLData.json."""

    settings: dict[str, str | int | bool] = Field(default_factory=dict)
    game_data: dict[str, Any] = Field(default_factory=dict)


def _restore_from_template(value: Any, template: Any) -> Any:
    if isinstance(template, set):
        if isinstance(value, (list, tuple, set)):
            return set(value)
        if value is None:
            return set()
        return {value}

    if isinstance(template, dict):
        incoming = value if isinstance(value, dict) else {}
        restored: dict[Any, Any] = {}

        for key, default_item in template.items():
            restored[key] = _restore_from_template(incoming.get(key), default_item)

        for key, raw_item in incoming.items():
            if key not in restored:
                restored[key] = deepcopy(raw_item)

        return restored

    if isinstance(template, list):
        if isinstance(value, list):
            return deepcopy(value)
        return deepcopy(template)

    if value is None:
        return deepcopy(template)
    return deepcopy(value)


class GameBase(GameResponse):
    """Utility base model shared by game implementations."""

    game_data: dict[str, Any] = Field(default_factory=dict)
    default_game_data: dict = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        """Create instance-local settings and initialize them from defaults."""
        self.settings_form = {
            key: item.model_copy(deep=True)
            for key, item in self.settings_form.items()
        }
        self.apply_settings(self.settings if self.settings else None)
        self.apply_game_data(self.game_data if self.game_data else None)

    def apply_settings(self, settings: dict[str, Any] | None = None) -> None:
        """Apply setting values and keep settings form values in sync."""
        incoming = settings or {}
        applied: dict[str, str | int | bool] = {}

        for key, item in self.settings_form.items():
            value = incoming.get(key, item.default)
            item.value = item.normalize_value(value)
            applied[key] = item.value if item.value is not None else item.default

        self.settings = applied

    def apply_game_data(self, game_data: dict[str, Any] | None = None) -> None:
        """Apply runtime game data with default-template restoration."""
        incoming = game_data or {}
        self.game_data = _restore_from_template(incoming, self.default_game_data)

    def apply_persisted_state(self, persisted: GamePersistedState) -> None:
        """Apply persisted settings and runtime data to this game instance."""
        self.apply_settings(persisted.settings)
        self.apply_game_data(persisted.game_data)

    def get_persisted_state(self) -> GamePersistedState:
        """Return minimal persisted state for this game instance."""
        return GamePersistedState(
            settings=self.settings,
            game_data=deepcopy(self.game_data),
        )

    def reset_game_data(self) -> dict[str, Any]:
        """Reset runtime game data to defaults and return a deep copy."""
        self.game_data = deepcopy(self.default_game_data)
        return deepcopy(self.game_data)