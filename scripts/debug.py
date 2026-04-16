#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add parent directory to path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.games.hide import HideGame

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "SLData.json"
LOCAL_GAMES_DIR = ROOT / "games"


class _BytesReader:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload


@dataclass
class _FakeTransport:
    ip: str

    def getpeername(self) -> tuple[str, int]:
        return (self.ip, 22)


class LocalDebugSSHClient:
    """A tiny SSH-client-like adapter used to run hide.check locally."""

    def __init__(self, home_dir: Path, ip: str):
        self.home_dir = home_dir
        self._transport = _FakeTransport(ip=ip)

    def get_transport(self) -> _FakeTransport:
        return self._transport

    def exec_command(self, command: str):
        env = dict(os.environ)
        env["HOME"] = str(self.home_dir)
        result = subprocess.run(
            command,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            env=env,
            check=False,
        )
        stdout = _BytesReader(result.stdout)
        stderr = _BytesReader(result.stderr)
        return None, stdout, stderr


def load_state() -> dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    state = load_state()
    hide_settings = state.get("games", {}).get("hide", {}).get("settings", {})
    users: dict[str, dict[str, Any]] = state.get("users", {})

    game = HideGame()
    game.apply_settings(hide_settings)

    print("Hide settings used for debug run:")
    print(json.dumps(hide_settings, ensure_ascii=False, indent=2))
    print()

    checked = 0
    completed = 0

    for ip, user in users.items():
        name = str(user.get("name") or ip)
        game_data = dict(user.get("gameData") or {})

        user_home = LOCAL_GAMES_DIR / name
        fake_client = LocalDebugSSHClient(home_dir=user_home, ip=ip)

        score = game.check(fake_client, game_data)
        done = bool(game_data.get("completed", False))

        checked += 1
        completed += int(done)

        print(
            f"[{ip}] {name}: "
            f"score={score}, completed={done}, "
            f"path={user_home / 'Game'}"
        )

    print()
    print(f"Summary: checked={checked}, completed={completed}, not_completed={checked - completed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
