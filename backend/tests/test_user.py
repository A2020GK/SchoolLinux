from __future__ import annotations

from typing import Any

import pytest

from backend.app.services import user as user_service
from backend.app.socket.manager import manager
from backend.tests.helpers import headers


@pytest.fixture(autouse=True)
def stub_ssh_check(monkeypatch):
    monkeypatch.setattr(user_service, "check_ip", lambda _ip: True)


def test_ping(client):
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == "pong"


def test_user_can_register_and_teacher_gets_update(client, monkeypatch):
    captured: dict[str, Any] = {}

    async def fake_send_to_teacher(event: str, data: Any) -> bool:
        captured["event"] = event
        captured["data"] = data
        return True

    monkeypatch.setattr(manager, "send_to_teacher", fake_send_to_teacher)

    response = client.post(
        "/user/register",
        json={"name": "Alex", "pcName": "pc-01"},
        headers=headers("10.0.0.11"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "isTeacher": False,
        "user": {"name": "Alex", "pcName": "pc-01", "score": 0, "kicked": False},
    }
    assert captured["event"] == "users_update"
    assert isinstance(captured["data"], dict)
    assert "10.0.0.11" in captured["data"]


def test_user_can_get_own_profile(client):
    register_response = client.post(
        "/user/register",
        json={"name": "Alex", "pcName": "pc-01"},
        headers=headers("10.0.0.12"),
    )
    assert register_response.status_code == 200

    me_response = client.get("/user/me", headers=headers("10.0.0.12"))

    assert me_response.status_code == 200
    assert me_response.json() == {
        "isTeacher": False,
        "user": {"name": "Alex", "pcName": "pc-01", "score": 0, "kicked": False},
    }


def test_teacher_can_get_all_users(client):
    first = client.post(
        "/user/register",
        json={"name": "Alex", "pcName": "pc-01"},
        headers=headers("10.0.0.21"),
    )
    second = client.post(
        "/user/register",
        json={"name": "Bob", "pcName": "pc-02"},
        headers=headers("10.0.0.22"),
    )
    assert first.status_code == 200
    assert second.status_code == 200

    response = client.get("/user/all", headers=headers("127.0.0.1"))

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert len(payload) == 2
    assert set(payload.keys()) == {"10.0.0.21", "10.0.0.22"}


def test_teacher_can_kick_and_unkick_user_and_user_gets_updates(client, monkeypatch):
    captured: list[dict[str, Any]] = []

    async def fake_send_to_ip(ip: str, event: str, data: Any) -> bool:
        captured.append({"ip": ip, "event": event, "data": data})
        return True

    monkeypatch.setattr(manager, "send_to_ip", fake_send_to_ip)

    register_response = client.post(
        "/user/register",
        json={"name": "Alex", "pcName": "pc-01"},
        headers=headers("10.0.0.33"),
    )
    assert register_response.status_code == 200
    captured.clear()

    kick_response = client.post(
        "/user/kick/10.0.0.33",
        json=True,
        headers=headers("127.0.0.1"),
    )
    unkick_response = client.post(
        "/user/kick/10.0.0.33",
        json=False,
        headers=headers("127.0.0.1"),
    )

    assert kick_response.status_code == 200
    assert kick_response.json() == {
        "name": "Alex",
        "pcName": "pc-01",
        "score": 0,
        "kicked": True,
    }
    assert unkick_response.status_code == 200
    assert unkick_response.json() == {
        "name": "Alex",
        "pcName": "pc-01",
        "score": 0,
        "kicked": False,
    }

    assert captured == [
        {"ip": "10.0.0.33", "event": "kicked", "data": {"kicked": True}},
        {"ip": "10.0.0.33", "event": "kicked", "data": {"kicked": False}},
    ]