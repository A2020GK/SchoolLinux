from __future__ import annotations

from typing import Any
from types import SimpleNamespace

from backend.app.routers import game as game_router
from backend.app.schemas.user import User
from backend.app.socket.manager import manager
from backend.app.state import state
from backend.tests.helpers import headers


def test_teacher_can_get_all_games(client):
    response = client.get("/game/list", headers=headers("127.0.0.1"))

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert len(payload) >= 1
    assert all("name" in game for game in payload.values())


def test_teacher_can_select_game_and_get_it_as_current(client):
    set_response = client.post(
        "/game/",
        json={"gameKey": "find", "settings": None},
        headers=headers("127.0.0.1"),
    )

    assert set_response.status_code == 200
    selected = set_response.json()
    assert selected["name"]

    current_response = client.get("/game/", headers=headers("127.0.0.1"))

    assert current_response.status_code == 200
    assert current_response.json() == selected


def test_check_allows_non_string_games_and_emits_users_update_on_score_change(client, monkeypatch):
    captured: dict[str, Any] = {}
    ip = "10.0.0.50"

    state.data.users[ip] = User(name="Alex", pc_name="pc-01", score=1, kicked=False, game_data={})

    monkeypatch.setattr(
        game_router,
        "get_current_game_service",
        lambda: SimpleNamespace(string_submission=False),
    )

    def fake_check_service(target_ip: str, _submission: str) -> int:
        state.data.users[target_ip].score = 5
        return 5

    monkeypatch.setattr(game_router, "check_service", fake_check_service)

    async def fake_send_to_teacher(event: str, data: Any) -> bool:
        captured["event"] = event
        captured["data"] = data
        return True

    monkeypatch.setattr(manager, "send_to_teacher", fake_send_to_teacher)

    response = client.post("/game/check", json="", headers=headers(ip))

    assert response.status_code == 200
    assert response.json() == 5
    assert captured["event"] == "users_update"
    assert ip in captured["data"]


def test_check_does_not_emit_users_update_when_score_is_unchanged(client, monkeypatch):
    called = {"value": False}
    ip = "10.0.0.51"

    state.data.users[ip] = User(name="Alex", pc_name="pc-02", score=0, kicked=False, game_data={})

    monkeypatch.setattr(
        game_router,
        "get_current_game_service",
        lambda: SimpleNamespace(string_submission=False),
    )

    def fake_check_service(target_ip: str, _submission: str) -> int:
        return state.data.users[target_ip].score

    monkeypatch.setattr(game_router, "check_service", fake_check_service)

    async def fake_send_to_teacher(event: str, data: Any) -> bool:
        called["value"] = True
        return True

    monkeypatch.setattr(manager, "send_to_teacher", fake_send_to_teacher)

    response = client.post("/game/check", json="", headers=headers(ip))

    assert response.status_code == 200
    assert response.json() == 0
    assert called["value"] is False


def test_start_requires_selected_game(client):
    response = client.post("/game/start", headers=headers("127.0.0.1"))

    assert response.status_code == 404
    assert response.json()["detail"] == "No game is currently selected"


def test_start_sets_running_and_stop_returns_to_idle(client):
    set_response = client.post(
        "/game/",
        json={"gameKey": "find", "settings": None},
        headers=headers("127.0.0.1"),
    )
    assert set_response.status_code == 200

    start_response = client.post("/game/start", headers=headers("127.0.0.1"))
    assert start_response.status_code == 200

    state_running_response = client.get("/game/state", headers=headers("127.0.0.1"))
    assert state_running_response.status_code == 200
    assert state_running_response.json() == {"state": "running"}

    stop_response = client.post("/game/stop", headers=headers("127.0.0.1"))
    assert stop_response.status_code == 200

    state_idle_response = client.get("/game/state", headers=headers("127.0.0.1"))
    assert state_idle_response.status_code == 200
    assert state_idle_response.json() == {"state": "idle"}


def test_start_emits_users_update_with_reset_scores(client, monkeypatch):
    sent: dict[str, Any] = {}
    student_updates: list[tuple[str, str, Any]] = []
    ip = "10.0.0.52"

    state.data.users[ip] = User(name="Alex", pc_name="pc-03", score=11, kicked=False, game_data={})

    async def fake_send_to_everyone(_event: str, _payload: Any) -> None:
        return None

    async def fake_send_to_teacher(event: str, data: Any) -> bool:
        sent["event"] = event
        sent["data"] = data
        return True

    async def fake_send_to_ip(target_ip: str, event: str, data: Any) -> bool:
        student_updates.append((target_ip, event, data))
        return True

    def fake_start_service() -> None:
        for user in state.data.users.values():
            user.score = 0

    monkeypatch.setattr(manager, "send_to_everyone", fake_send_to_everyone)
    monkeypatch.setattr(manager, "send_to_teacher", fake_send_to_teacher)
    monkeypatch.setattr(manager, "send_to_ip", fake_send_to_ip)
    monkeypatch.setattr(game_router, "start_game_service", fake_start_service)

    set_response = client.post(
        "/game/",
        json={"gameKey": "find", "settings": None},
        headers=headers("127.0.0.1"),
    )
    assert set_response.status_code == 200

    start_response = client.post("/game/start", headers=headers("127.0.0.1"))

    assert start_response.status_code == 200
    assert sent["event"] == "users_update"
    assert sent["data"][ip]["score"] == 0
    assert (ip, "user_update", sent["data"][ip]) in student_updates


def test_start_transitions_through_init_before_running(client, monkeypatch):
    states: list[str] = []

    async def fake_send_to_students(event: str, payload: Any) -> None:
        if event == "game_state_changed":
            states.append(payload["state"])

    def fake_start_service() -> None:
        assert state.data.state == "init"

    monkeypatch.setattr(manager, "send_to_everyone", fake_send_to_students)
    monkeypatch.setattr(game_router, "start_game_service", fake_start_service)

    set_response = client.post(
        "/game/",
        json={"gameKey": "find", "settings": None},
        headers=headers("127.0.0.1"),
    )
    assert set_response.status_code == 200

    start_response = client.post("/game/start", headers=headers("127.0.0.1"))
    assert start_response.status_code == 200
    assert states == ["init", "running"]
    assert state.data.state == "running"