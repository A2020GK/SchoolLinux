from __future__ import annotations

from backend.app.games import Game, GameSettingsItem
from backend.app.schemas.user import User
from backend.app.services import game as game_service
from backend.app.state import state


class DummyStringGame(Game):
    name: str = "Dummy"
    description: str = "Dummy game"
    string_submission: bool = True
    settings_form: dict[str, GameSettingsItem] = {
        "limit": GameSettingsItem(name="Limit", type="number", default=1),
    }

    def install(self, client, game_data):
        return None

    def check_string_submission(self, submission, game_data):
        return 2 if submission == "ok" else 0

    def check(self, client, game_data):
        return 0

    def uninstall(self, client, game_data):
        return None


def test_set_current_game_updates_state_and_returns_response(isolated_state, monkeypatch):
    dummy = DummyStringGame()
    monkeypatch.setattr(game_service, "games", {"dummy": dummy})
    state.data.games = {"dummy": dummy.get_persisted_state()}

    response = game_service.set_current_game("dummy", {"limit": "3"})

    assert response.name == "Dummy"
    assert response.settings["limit"] == 3
    assert state.data.current_game == "dummy"
    assert state.data.games["dummy"].settings["limit"] == 3


def test_set_current_game_raises_for_unknown_game(isolated_state, monkeypatch):
    monkeypatch.setattr(game_service, "games", {})

    try:
        game_service.set_current_game("missing", None)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_get_current_game_response_safe_hides_internal_fields(isolated_state, monkeypatch):
    dummy = DummyStringGame()
    monkeypatch.setattr(game_service, "games", {"dummy": dummy})
    state.data.games = {"dummy": dummy.get_persisted_state()}
    state.data.current_game = "dummy"

    response = game_service.get_current_game_response(safe=True)

    assert response is not None
    payload = response.model_dump(by_alias=True)
    assert "settingsForm" not in payload
    assert "anticheatRequired" not in payload


def test_check_returns_zero_for_unknown_user(isolated_state, monkeypatch):
    dummy = DummyStringGame()
    monkeypatch.setattr(game_service, "games", {"dummy": dummy})
    state.data.games = {"dummy": dummy.get_persisted_state()}
    state.data.current_game = "dummy"

    assert game_service.check("10.0.0.200", "ok") == 0


def test_check_updates_user_score_for_string_submission(isolated_state, monkeypatch):
    dummy = DummyStringGame()
    monkeypatch.setattr(game_service, "games", {"dummy": dummy})
    monkeypatch.setattr(game_service, "create_client_from_config", lambda _ip: object())

    ip = "10.0.0.201"
    state.data.games = {"dummy": dummy.get_persisted_state()}
    state.data.current_game = "dummy"
    state.data.users[ip] = User(name="Alex", pc_name="pc-1", score=0, kicked=False, game_data={})

    score = game_service.check(ip, "ok")

    assert score == 2
    assert state.data.users[ip].score == 2
