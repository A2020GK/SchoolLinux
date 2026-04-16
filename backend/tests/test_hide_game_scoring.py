from __future__ import annotations

from typing import Any

from backend.app.games import hide as hide_module


def _metrics_stdout(metrics: dict[str, int]) -> str:
    ordered_keys = (
        "treasures",
        "files",
        "empty_files",
        "root_treasures",
        "root_dirs",
        "deep_root_dirs",
    )
    return "\n".join(f"{key}={metrics.get(key, 0)}" for key in ordered_keys)


def _run_hide_check(monkeypatch, *, metrics: dict[str, int], game_data: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    game = hide_module.HideGame()
    game.apply_settings(
        {
            "treasures_amount": 2,
            "stubs": 3,
            "allow_empty_stubs": False,
            "allow_root_treasures": False,
            "root_folders": 5,
            "depth_folders": 1,
            "depth": 3,
        }
    )

    stdout = _metrics_stdout(metrics)
    monkeypatch.setattr(hide_module, "execute_command", lambda _client, _command: (stdout, ""))

    payload = {} if game_data is None else game_data
    score = game.check(client=object(), game_data=payload)
    return score, payload


def test_hide_scoring_perfect_submission_returns_10_and_marks_completed(monkeypatch):
    score, game_data = _run_hide_check(
        monkeypatch,
        metrics={
            "treasures": 2,
            "files": 5,
            "empty_files": 0,
            "root_treasures": 0,
            "root_dirs": 5,
            "deep_root_dirs": 2,
        },
    )

    assert score == 10
    assert game_data["completed"] is True


def test_hide_scoring_applies_treasure_deviation_and_stub_penalties(monkeypatch):
    score, game_data = _run_hide_check(
        monkeypatch,
        metrics={
            "treasures": 1,
            "files": 3,
            "empty_files": 0,
            "root_treasures": 0,
            "root_dirs": 1,
            "deep_root_dirs": 1,
        },
    )

    assert score == 6
    assert "completed" not in game_data


def test_hide_scoring_applies_deep_structure_penalty(monkeypatch):
    score, game_data = _run_hide_check(
        monkeypatch,
        metrics={
            "treasures": 2,
            "files": 5,
            "empty_files": 0,
            "root_treasures": 0,
            "root_dirs": 0,
            "deep_root_dirs": 0,
        },
    )

    assert score == 9
    assert game_data["completed"] is True


def test_hide_scoring_applies_rule_violation_penalties_and_clamps_at_zero(monkeypatch):
    score, game_data = _run_hide_check(
        monkeypatch,
        metrics={
            "treasures": 0,
            "files": 0,
            "empty_files": 4,
            "root_treasures": 3,
            "root_dirs": 0,
            "deep_root_dirs": 0,
        },
    )

    assert score == 0
    assert "completed" not in game_data


def test_hide_scoring_keeps_rechecking_even_when_completed_is_already_true(monkeypatch):
    score, game_data = _run_hide_check(
        monkeypatch,
        metrics={
            "treasures": 0,
            "files": 0,
            "empty_files": 1,
            "root_treasures": 1,
            "root_dirs": 0,
            "deep_root_dirs": 0,
        },
        game_data={"completed": True},
    )

    assert score == 0
    assert game_data["completed"] is True
