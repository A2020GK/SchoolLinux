from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from backend.app.config import config
from backend.app.dependencies.user import _get_request_ip, teacher_only


def _request(headers: dict[str, str] | None = None, client_host: str | None = "10.1.1.1") -> Request:
    raw_headers = []
    for key, value in (headers or {}).items():
        raw_headers.append((key.lower().encode("utf-8"), value.encode("utf-8")))

    scope = {
        "type": "http",
        "headers": raw_headers,
        "method": "GET",
        "path": "/",
    }
    if client_host is not None:
        scope["client"] = (client_host, 12345)

    return Request(scope)


def test_get_request_ip_prefers_override_header(monkeypatch):
    monkeypatch.setattr(config, "allow_ip_override", True)
    request = _request(headers={config.ip_override_header: "10.9.9.9"}, client_host="10.1.1.1")

    ip = _get_request_ip(request)

    assert ip == "10.9.9.9"


def test_get_request_ip_uses_client_host_when_override_disabled(monkeypatch):
    monkeypatch.setattr(config, "allow_ip_override", False)
    request = _request(headers={config.ip_override_header: "10.9.9.9"}, client_host="10.1.1.1")

    ip = _get_request_ip(request)

    assert ip == "10.1.1.1"


def test_get_request_ip_falls_back_to_loopback(monkeypatch):
    monkeypatch.setattr(config, "allow_ip_override", False)
    request = _request(client_host=None)

    ip = _get_request_ip(request)

    assert ip == "127.0.0.1"


def test_teacher_only_rejects_non_teacher():
    with pytest.raises(HTTPException):
        teacher_only(False)
