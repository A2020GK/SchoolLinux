from __future__ import annotations

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