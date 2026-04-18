from __future__ import annotations

import pytest

import backend.app.games.find as find_game_module
from backend.app.games.find import FindGame


def test_apply_settings_updates_required_user_score():
    game = FindGame()

    game.apply_settings({"treasures_amount": 7})

    assert game.required_user_score == 7


def test_apply_settings_does_not_raise_on_extreme_values():
    game = FindGame()

    game.apply_settings(
        {
            "treasures_amount": 0,
            "files_amount": 1,
            "max_depth": 0,
            "content_lines": 1,
            "gzip_percent": 1000,
        }
    )

    assert game.required_user_score == 1


def test_check_string_submission_normalizes_and_counts_only_once():
    game = FindGame()
    game_data = {"hidden_klads": {"klad:red blue green"}}

    first = game.check_string_submission("  KLAD:   red   blue green  ", game_data)
    second = game.check_string_submission("klad:red blue green", game_data)

    assert first == 1
    assert second == 0
    assert game_data["hidden_klads"] == set()


def test_install_populates_hidden_klads_and_uses_script_helper(monkeypatch):
    game = FindGame()
    game.apply_settings(
        {
            "treasures_amount": 2,
            "files_amount": 3,
            "max_depth": 2,
            "content_lines": 4,
            "gzip_percent": 0,
        }
    )

    captured: dict[str, str] = {}

    def fake_upload_and_run_script(_client, name: str, script: str):
        captured["name"] = name
        captured["script"] = script
        return None, None

    monkeypatch.setattr(find_game_module, "upload_and_run_script", fake_upload_and_run_script)

    game_data: dict = {}
    game.install(object(), game_data)

    assert captured["name"] == "find_game_install"
    assert "set -euo pipefail" in captured["script"]
    assert 'ROOT="$HOME/Game"' in captured["script"]
    assert len(game_data["hidden_klads"]) == 2
    assert all(pattern.startswith("klad:") for pattern in game_data["hidden_klads"])


def test_uninstall_uses_execute_command(monkeypatch):
    game = FindGame()
    captured: dict[str, str] = {}

    def fake_execute_command(_client, command: str):
        captured["command"] = command
        return "", ""

    monkeypatch.setattr(find_game_module, "execute_command", fake_execute_command)

    game.uninstall(object(), {})

    assert captured["command"] == 'rm -rf "$HOME/Game"'
