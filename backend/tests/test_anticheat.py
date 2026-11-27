from __future__ import annotations

from backend.app.games import Game
from backend.app.schemas.user import User
from backend.app.services import anticheat
from backend.app.services import game as game_service
from backend.app.state import state


class AnticheatGame(Game):
    name: str = "Anticheat"
    description: str = "Anticheat game"
    string_submission: bool = False
    anticheat_required: bool = True

    def install(self, client, game_data):
        game_data["installed"] = True

    def check(self, client, game_data):
        return 0

    def uninstall(self, client, game_data):
        return None


class NoAnticheatGame(AnticheatGame):
    name: str = "No anticheat"
    anticheat_required: bool = False


class DummyClient:
    def close(self):
        return None


def _select_game(monkeypatch, game: Game, game_key: str) -> None:
    monkeypatch.setattr(game_service, "games", {game_key: game})
    state.data.games = {game_key: game.get_persisted_state()}
    state.data.current_game = game_key


def test_start_anticheat_stops_old_instance_uploads_and_launches(monkeypatch):
    client = object()
    calls: dict[str, object] = {}

    def fake_stop(_client):
        calls["stopped"] = _client

    def fake_upload(_client, name, script):
        calls["upload"] = (name, script)
        return anticheat.SCRIPT_PATH

    def fake_execute(_client, command):
        calls["command"] = command
        return "4321\n", ""

    monkeypatch.setattr(anticheat, "stop_anticheat", fake_stop)
    monkeypatch.setattr(anticheat, "upload_script", fake_upload)
    monkeypatch.setattr(anticheat, "execute_command", fake_execute)

    pid = anticheat.start_anticheat(client)

    assert pid == 4321
    assert calls["stopped"] is client
    assert calls["upload"] == (anticheat.SCRIPT_NAME, anticheat.ANTICHEAT_SCRIPT)
    assert f"nohup bash {anticheat.SCRIPT_PATH}" in calls["command"]
    assert f">{anticheat.LOG_FILE}" in calls["command"]


def test_stop_anticheat_reads_pid_file_validates_process_and_removes_files(monkeypatch):
    calls: dict[str, str] = {}

    def fake_execute(_client, command):
        calls["command"] = command
        return "", ""

    monkeypatch.setattr(anticheat, "execute_command", fake_execute)

    anticheat.stop_anticheat(object())

    command = calls["command"]
    assert anticheat.PID_FILE in command
    assert anticheat.SCRIPT_PATH in command
    assert '"/proc/$pid/cmdline"' in command
    assert "kill -9" in command
    assert 'rm -f "$pid_file" "$script_path"' in command


def test_anticheat_script_contains_expected_targets_and_loop():
    script = anticheat.ANTICHEAT_SCRIPT

    for name in anticheat.FILE_MANAGERS:
        assert name in script

    assert "while true" in script
    assert "collect_descendants" in script
    assert "/proc/$pid/task/$pid/children" in script
    assert 'echo "$$" > "$PID_FILE"' in script
    assert "kill -9" in script
    assert "sleep 1" in script


def test_start_game_starts_anticheat_when_required(isolated_state, monkeypatch):
    game = AnticheatGame()
    _select_game(monkeypatch, game, "anticheat")
    state.data.users["10.0.0.30"] = User(
        name="Alex",
        pc_name="pc-30",
        score=0,
        kicked=False,
        game_data={},
    )

    started: list[object] = []
    monkeypatch.setattr(game_service, "create_client_from_config", lambda _ip: DummyClient())
    monkeypatch.setattr(game_service, "start_anticheat", lambda client: started.append(client))

    game_service.start_game()

    assert len(started) == 1


def test_start_game_skips_anticheat_when_not_required(isolated_state, monkeypatch):
    game = NoAnticheatGame()
    _select_game(monkeypatch, game, "no_anticheat")
    state.data.users["10.0.0.31"] = User(
        name="Mia",
        pc_name="pc-31",
        score=0,
        kicked=False,
        game_data={},
    )

    started: list[object] = []
    monkeypatch.setattr(game_service, "create_client_from_config", lambda _ip: DummyClient())
    monkeypatch.setattr(game_service, "start_anticheat", lambda client: started.append(client))

    game_service.start_game()

    assert started == []


def test_stop_game_stops_anticheat_even_when_uninstall_fails(isolated_state, monkeypatch):
    class FailingUninstallGame(AnticheatGame):
        def uninstall(self, client, game_data):
            raise RuntimeError("uninstall failed")

    game = FailingUninstallGame()
    _select_game(monkeypatch, game, "failing_uninstall")
    state.data.users["10.0.0.32"] = User(
        name="Sam",
        pc_name="pc-32",
        score=0,
        kicked=False,
        game_data={},
    )

    stopped: list[object] = []
    monkeypatch.setattr(game_service, "create_client_from_config", lambda _ip: DummyClient())
    monkeypatch.setattr(game_service, "stop_anticheat", lambda client: stopped.append(client))

    game_service.stop_game()

    assert len(stopped) == 1
