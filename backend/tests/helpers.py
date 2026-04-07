from __future__ import annotations

from backend.app.config import config


def headers(ip: str) -> dict[str, str]:
    return {config.ip_override_header: ip}