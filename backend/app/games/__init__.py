"""Teacher-facing game API.

Write custom games by inheriting Game from this module:
from backend.app.games import Game, GameSettingsItem
"""

from typing import Any

from paramiko import SSHClient
from pydantic import Field

from ..schemas.game import GameBase, GameSettingsItem
from backend.app.services.ssh import *

class Game(GameBase):
    """Base class for custom games.

    Teacher-facing metadata fields:
    - name
    - description
    - settings_form
    - settings
    - string_submission
    - anticheat_required
    - default_game_data
    - required_user_score
    """

    # Metadata visible to teacher and student UI.
    name: str = "Base Game"
    description: str = "Base game description"

    # Runtime and scoring behavior.
    string_submission: bool = False
    anticheat_required: bool = False
    required_user_score: int = 0

    # Declarative game configuration.
    settings_form: dict[str, GameSettingsItem] = Field(default_factory=dict)
    settings: dict[str, str | int | bool] = Field(default_factory=dict)

    # Per-student state template for a new start.
    default_game_data: dict = Field(default_factory=dict)

    def install(self, client: SSHClient, game_data: dict[str, Any]) -> None:
        """Create and install game files on the student's machine."""
        raise NotImplementedError

    def check_string_submission(self, submission: str, game_data: dict[str, Any]) -> int:
        """Validate a text answer and return score delta.

        Called only when string_submission is True.
        """
        raise NotImplementedError

    def check(self, client: SSHClient, game_data: dict[str, Any]) -> int:
        """Validate game completion and return score delta.

        Called only when string_submission is False.
        """
        raise NotImplementedError

    def uninstall(self, client: SSHClient, game_data: dict[str, Any]) -> None:
        """Remove files created by the game from the student's machine."""
        raise NotImplementedError


__all__ = ["Game", "GameSettingsItem"]
