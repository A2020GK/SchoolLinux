from __future__ import annotations

import json

import pytest

from backend.app.helpers.json_safe_value import _json_safe_value
from backend.app.schemas.game import GamePersistedState
from backend.app.schemas.user import RegisterRequest, User
from backend.app.services import user as user_service
from backend.app.state import AppData, StateManager, _is_valid_game_key, state


def test_json_safe_value_normalizes_collections():
    payload = {
        "set": {3, 1},
        "tuple": ("a", 2),
        99: {"inner": {"z", "a"}},
    }

    converted = _json_safe_value(payload)

    assert converted["set"] == [1, 3]
    assert converted["tuple"] == ["a", 2]
    assert converted["99"]["inner"] == ["a", "z"]


def test_game_key_validator_accepts_reasonable_keys():
    assert _is_valid_game_key("find") is True
    assert _is_valid_game_key("hide_game-1") is True
    assert _is_valid_game_key("bad key") is False
    assert _is_valid_game_key("bad/key") is False


def test_app_data_rejects_invalid_current_game_reference():
    with pytest.raises(ValueError):
        AppData(current_game="missing", games={"find": GamePersistedState(settings={})})


def test_state_manager_sanitizes_invalid_games_payload(tmp_path):
    path = tmp_path / "SLData.test.json"
    path.write_text(
        json.dumps(
            {
                "currentGame": "bad key",
                "games": {
                    "good_key": {"settings": {"level": 2}},
                    "bad key": {"settings": {"x": 1}},
                    "broken": {"settings": "not-a-dict"},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manager = StateManager(path)

    assert set(manager.data.games.keys()) == {"good_key"}
    assert manager.data.current_game is None


def test_register_user_returns_existing_user_without_recheck(isolated_state, monkeypatch):
    ip = "10.0.0.61"
    existing = User(name="Alex", pc_name="pc-01", score=3, kicked=False, game_data={})
    state.data.users[ip] = existing

    called = {"count": 0}

    def fake_check(_ip: str) -> bool:
        called["count"] += 1
        return True

    monkeypatch.setattr(user_service, "check_ip", fake_check)

    user, created = user_service.register_user(RegisterRequest(name="Alex", pc_name="pc-01"), ip)

    assert user is existing
    assert created is False
    assert called["count"] == 0


def test_register_user_raises_when_ssh_unreachable(isolated_state, monkeypatch):
    monkeypatch.setattr(user_service, "check_ip", lambda _ip: False)

    with pytest.raises(ValueError):
        user_service.register_user(RegisterRequest(name="Alex", pc_name="pc-01"), "10.0.0.62")


def test_register_user_saves_new_user_with_pc_name(isolated_state, monkeypatch):
    monkeypatch.setattr(user_service, "check_ip", lambda _ip: True)

    user, created = user_service.register_user(RegisterRequest(name="Alex", pc_name="pc-42"), "10.0.0.63")

    assert created is True
    assert user is not None
    assert user.name == "Alex"
    assert user.pc_name == "pc-42"
    assert user.score == 0
    assert state.data.users["10.0.0.63"].pc_name == "pc-42"


def test_set_kicked_returns_false_for_unknown_user(isolated_state):
    assert user_service.set_kicked("10.0.0.99", True) is False
