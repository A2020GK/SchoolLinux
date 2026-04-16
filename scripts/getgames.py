#!/usr/bin/env python3
import json
import shutil
import stat
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "SLData.json"
OUT_ROOT = ROOT / "games"

USERNAME = "game"
PASSWORD = "game"
REMOTE_GAME_DIR = "/home/game/Game"
TIMEOUT = 7


def safe_name(name: str) -> str:
    cleaned = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    cleaned = cleaned.strip()
    return cleaned or "unknown_user"


def download_tree(sftp: paramiko.SFTPClient, remote_dir: str, local_dir: Path) -> None:
    for entry in sftp.listdir_attr(remote_dir):
        remote_path = f"{remote_dir}/{entry.filename}"
        local_path = local_dir / entry.filename

        if stat.S_ISDIR(entry.st_mode):
            local_path.mkdir(parents=True, exist_ok=True)
            download_tree(sftp, remote_path, local_path)
        else:
            sftp.get(remote_path, str(local_path))


def main() -> int:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    users = data.get("users", {})
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    ok = 0
    failed = 0

    for ip, user_data in users.items():
        name = safe_name(str(user_data.get("name", ip)))
        local_game_dir = OUT_ROOT / name / "Game"

        if local_game_dir.exists():
            shutil.rmtree(local_game_dir)
        local_game_dir.mkdir(parents=True, exist_ok=True)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(
                ip,
                username=USERNAME,
                password=PASSWORD,
                timeout=TIMEOUT,
                auth_timeout=TIMEOUT,
                banner_timeout=TIMEOUT,
            )
            sftp = ssh.open_sftp()
            try:
                sftp.stat(REMOTE_GAME_DIR)
                download_tree(sftp, REMOTE_GAME_DIR, local_game_dir)
                print(f"[OK] {ip} -> {local_game_dir}")
                ok += 1
            finally:
                sftp.close()
        except Exception as exc:
            print(f"[FAIL] {ip} ({name}): {exc}")
            failed += 1
        finally:
            ssh.close()

    print(f"Done. success={ok}, failed={failed}, total={len(users)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
