from __future__ import annotations

import pytest

import backend.app.games.find as find_game_module
from backend.app.games.find import FindGame


def _extract_script_files(script: str) -> tuple[dict[str, list[str]], set[str]]:
    files: dict[str, list[str]] = {}
    gzipped: set[str] = set()
    lines = script.splitlines()
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        if line.startswith('cat > "$ROOT/') and line.endswith('" << \'EOF_FIND\''):
            rel_path = line[len('cat > "$ROOT/'):-len('" << \'EOF_FIND\'')]
            idx += 1

            content: list[str] = []
            while idx < len(lines) and lines[idx] != "EOF_FIND":
                content.append(lines[idx])
                idx += 1

            assert idx < len(lines), "Generated script has unterminated here-doc"
            idx += 1

            if idx + 2 < len(lines) and lines[idx] == "if command -v gzip >/dev/null 2>&1; then":
                assert lines[idx + 1] == f'  gzip -f "$ROOT/{rel_path}"'
                assert lines[idx + 2] == "fi"
                gzipped.add(rel_path)
                idx += 3

            files[rel_path] = content
            continue

        idx += 1

    return files, gzipped


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


def test_check_string_submission_normalizes_hidden_klads_list_payload():
    game = FindGame()
    game_data = {
        "hidden_klads": [
            "  KLAD:  red  blue green ",
            "other_value",
        ]
    }

    score = game.check_string_submission("klad:red blue green", game_data)

    assert score == 1
    assert "klad:red blue green" not in game_data["hidden_klads"]
    assert "other_value" in game_data["hidden_klads"]


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


def test_install_generates_requested_amount_of_files(monkeypatch):
    game = FindGame()
    game.apply_settings(
        {
            "treasures_amount": 3,
            "files_amount": 12,
            "max_depth": 3,
            "content_lines": 5,
            "gzip_percent": 0,
        }
    )

    captured: dict[str, str] = {}

    def fake_upload_and_run_script(_client, _name: str, script: str):
        captured["script"] = script
        return None, None

    monkeypatch.setattr(find_game_module, "upload_and_run_script", fake_upload_and_run_script)

    game_data: dict = {}
    game.install(object(), game_data)

    files, gzipped = _extract_script_files(captured["script"])
    treasure_files = [path for path, lines in files.items() if lines and lines[0].startswith("klad:")]

    assert len(files) == 12
    assert len(set(files)) == 12
    assert len(gzipped) == 0
    assert len(treasure_files) == 3


def test_install_gzip_100_keeps_at_least_one_treasure_plain_text(monkeypatch):
    game = FindGame()
    game.apply_settings(
        {
            "treasures_amount": 4,
            "files_amount": 9,
            "max_depth": 2,
            "content_lines": 4,
            "gzip_percent": 100,
        }
    )

    captured: dict[str, str] = {}

    def fake_upload_and_run_script(_client, _name: str, script: str):
        captured["script"] = script
        return None, None

    monkeypatch.setattr(find_game_module, "upload_and_run_script", fake_upload_and_run_script)

    game_data: dict = {}
    game.install(object(), game_data)

    files, gzipped = _extract_script_files(captured["script"])
    treasure_files = [path for path, lines in files.items() if lines and lines[0].startswith("klad:")]

    assert len(files) == 9
    assert len(treasure_files) == 4
    assert len(gzipped) == 8
    assert any(path not in gzipped for path in treasure_files)


def test_install_falls_back_when_random_paths_collide(monkeypatch):
    game = FindGame()
    game.apply_settings(
        {
            "treasures_amount": 2,
            "files_amount": 6,
            "max_depth": 2,
            "content_lines": 3,
            "gzip_percent": 0,
        }
    )

    captured: dict[str, str] = {}

    def fake_upload_and_run_script(_client, _name: str, script: str):
        captured["script"] = script
        return None, None

    monkeypatch.setattr(find_game_module, "upload_and_run_script", fake_upload_and_run_script)
    monkeypatch.setattr(game, "_mkname", lambda _words: "same")

    game_data: dict = {}
    game.install(object(), game_data)

    files, _ = _extract_script_files(captured["script"])

    assert len(files) == 6
    assert any(path.startswith("generated_") for path in files)


def test_generate_treasure_patterns_requires_three_unique_words():
    game = FindGame()

    with pytest.raises(ValueError, match="at least 3 unique words"):
        game._generate_treasure_patterns(["alpha", "alpha", "beta"], 1)


def test_generate_treasure_patterns_rejects_impossible_amount():
    game = FindGame()

    with pytest.raises(ValueError, match="Cannot generate"):
        game._generate_treasure_patterns(["alpha", "beta", "gamma"], 7)


def test_uninstall_uses_execute_command(monkeypatch):
    game = FindGame()
    captured: dict[str, str] = {}

    def fake_execute_command(_client, command: str):
        captured["command"] = command
        return "", ""

    monkeypatch.setattr(find_game_module, "execute_command", fake_execute_command)

    game.uninstall(object(), {})

    assert captured["command"] == 'rm -rf "$HOME/Game"'
