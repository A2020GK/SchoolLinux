# SchoolLinux Backend: Technical Documentation

## Stack and runtime
- **Language**: Python 3.12
- **Framework**: FastAPI (`backend/app/main.py`)
- **Realtime**: `python-socketio` in ASGI mode mounted at `/socket.io`
- **SSH integration**: `paramiko` for remote checks and game install/uninstall on student machines
- **State persistence**: JSON file `SLData.json` via typed `StateManager`
- **Validation/modeling**: Pydantic v2 (`BaseSchema`, game/user schemas)
- **Tests**: `pytest` (35 tests in `backend/tests`)

## Backend package layout
- `backend/app/main.py`: App creation, CORS, router mounting, lifespan boot sequence
- `backend/app/config.py`: Environment-driven settings using `BaseSettings`
- `backend/app/state.py`: Typed persistent state (`AppData`) + load/save/sanitize
- `backend/app/logging.py`: Logging bootstrap
- `backend/app/schemas/*`: API/persistence models
- `backend/app/services/*`: Business logic (users, games, SSH)
- `backend/app/routers/*`: HTTP API endpoints
- `backend/app/socket/*`: Socket.IO server, handlers, connection manager
- `backend/app/games/*`: Teacher-facing game plugin API + built-in game implementations
- `backend/app/helpers/json_safe_value.py`: JSON-safe conversion for set/tuple/etc.

## Application boot flow
1. `backend/app/main.py` imports logging config first.
2. FastAPI app is created with lifespan hook.
3. On startup lifespan:
   - `state.reload()` loads persisted JSON into `AppData`
   - `discover_and_load_games()` dynamically imports all game modules and hydrates settings from persisted state
4. Routers `/user` and `/game` are mounted.
5. Socket server is mounted at `/socket.io`.

## Configuration (`backend/app/config.py`)
`Config` fields:
- `ssh_user` (default `"game"`)
- `ssh_password` (default `"game"`)
- `ssh_timeout` (default `10.0`)
- `allow_ip_override` (default `False`) for dev/test IP spoofing
- `ip_override_header` (default `"X-Debug-IP"`)

Config source priority:
1. Environment variables
2. `.env`
3. Defaults

## Logging (`backend/app/logging.py`)
- Uvicorn loggers are adjusted before app import.
- Root logging configured with `StreamHandler`, debug level, tab-separated format:
  `LEVEL\tLOGGER\tMESSAGE\tTIME`

## State model and persistence (`backend/app/state.py`)

### `AppData`
- `current_game: str | None`
- `state: "idle" | "init" | "running"` (global game lifecycle)
- `games: dict[str, GamePersistedState]` (persisted settings per game key)
- `users: dict[str, User]` (indexed by client IP)

### Integrity rules
- Game keys must match regex `^[A-Za-z0-9_-]+$`
- `current_game` must exist in `games` if not null

### Loading behavior
- Missing file => empty `AppData`
- Invalid JSON => reset to empty in-memory state
- Invalid payload => sanitization path:
  - drops invalid game keys
  - drops invalid game payloads
  - normalizes `currentGame`/`current_game` alias
  - keeps only consistent values

### Save behavior
- Writes camelCase aliases (`model_dump(by_alias=True, mode="json")`)
- UTF-8 JSON with indentation

## Base schema conventions (`backend/app/schemas/base.py`)
All schemas inherit `BaseSchema`:
- snake_case fields map to camelCase JSON keys via alias generator (`to_camel`)
- `populate_by_name=True`
- `from_attributes=True`
- whitespace stripping and assignment validation enabled

## User domain

### Schemas (`backend/app/schemas/user.py`)
- `RegisterRequest`: `{ name, pc_name }`
- `SafeUserData`: register fields + `score`, `kicked`
- `User`: `SafeUserData` + internal `game_data`
- `UserResponse`: `{ is_teacher, user }` where `user` is null for teacher sessions

### Service (`backend/app/services/user.py`)
- Teacher detection = loopback IP (`ipaddress(ip).is_loopback`)
- Registration rules:
  - teachers cannot register as students
  - existing IP returns existing user without re-checking SSH
  - new user must pass SSH connectivity (`check_ip`)
  - persisted in state and saved
- Mutations:
  - `set_kicked(ip, bool)`
  - `delete_user(ip)`

### Dependency layer (`backend/app/dependencies/user.py`)
- `_get_request_ip`:
  - optional header override when `allow_ip_override=True`
  - else `request.client.host`
  - fallback `127.0.0.1`
- DI aliases:
  - `IpDep`, `CurrentUserDep`, `IsTeacherDep`, `TeacherOnlyDep`
- `teacher_only` raises HTTP 403 for non-loopback users

### User routes (`backend/app/routers/user.py`)
- `POST /user/register`
  - returns teacher response for loopback clients
  - student register path emits socket `users_update` to teacher when created
- `GET /user/all` (teacher-only)
- `GET /user/me`
- `DELETE /user/me` (students only), emits `users_update` when deleted
- `POST /user/kick/{ip}` (teacher-only)
  - toggles kicked state
  - emits socket `kicked` to target IP

## Game domain

### Game schemas (`backend/app/schemas/game.py`)
- `GameSettingsItem`:
  - `type`: `string | number | boolean | option`
  - strict normalization logic:
    - number => `int(raw)`
    - boolean => bool parser with textual variants (`true/1/yes/on`, etc.)
    - option => must be key in `options`
- `GameResponseSafe` (student-safe)
- `GameResponse` (teacher/full)
- `GameChangeRequest`: `{ game_key, settings? }`
- `GamePersistedState`: settings-only persistence payload
- `GameBase`:
  - deep-copies `settings_form` per instance
  - applies defaults/incoming settings
  - exposes `new_game_data()` using deep copy of template

### Plugin API (`backend/app/games/__init__.py`)
`Game` extends `GameBase` and defines teacher-facing contract:
- Metadata fields: `name`, `description`, `string_submission`, `anticheat_required`, `required_user_score`
- Config fields: `settings_form`, `settings`
- Runtime template: `default_game_data`
- Required methods:
  - `install(client, game_data)`
  - `check_string_submission(submission, game_data)` (for text-mode games)
  - `check(client, game_data)` (SSH-mode games)
  - `uninstall(client, game_data)`

`backend.app.games` re-exports SSH helper functions (`execute_command`, `upload_and_run_script`) via wildcard import from `services.ssh`.

### Dynamic discovery (`backend/app/services/game.py`)
- Scans `backend/app/games/*.py` excluding `_*.py`
- Loads each module via `importlib.util.spec_from_file_location`
- Finds subclasses of `Game`
- If multiple game classes in one file: first is used, others logged and ignored
- Re-applies persisted settings from `state.data.games[game_key]`
- Rebuilds persisted game map and saves state
- Resets `current_game` if no longer available

### Runtime game service logic
- `games` global in-memory map stores live game instances (not persisted)
- `set_current_game(game_key, settings)`:
  - validates key exists
  - updates current game and optional settings
  - persists sanitized settings (`_json_safe_value`)
- `start_game()`:
  - requires selected game
  - for each user: resets `user.game_data` with `new_game_data()`
  - opens SSH client, runs `game.install`, always closes client safely
  - errors per-user are logged and do not stop whole loop
- `stop_game()`:
  - for each user runs `game.uninstall` over SSH
- `check(ip, submission)`:
  - unknown user => returns `0`
  - no current game => returns existing user score
  - string game => increments score by returned delta
  - non-string game => sets score to result of SSH `check`
  - state saved on successful check

### Game routes (`backend/app/routers/game.py`)
- `GET /game/`: current game, safe/full based on caller role
- `GET /game/list`: teacher-only full catalog
- `POST /game/`: set game unless global state is `running` (409)
  - emits socket `game_change` to students (safe payload)
- `POST /game/check`:
  - requires selected game, existing user, not kicked
  - string submission body used only for string-mode games
  - emits `users_update` to teacher only when score changed
- `POST /game/start`:
  - only from global `idle`
  - transition `idle -> init -> running`
  - emits `game_state_changed` on each transition
  - rollback to idle on failure
- `POST /game/stop`:
  - only from `running`
  - runs stop service then sets `idle`, emits `game_state_changed`
- `GET /game/state`: returns lifecycle state

## Built-in games

### `find.py` (`FindGame`)
- String-submission game.
- Generates nested random directory tree and text/gzip files in `$HOME/Game`.
- Randomly hides `klad:<3 random words>` patterns in treasure files.
- Stores remaining valid treasure strings in `game_data["hidden_klads"]` (set).
- Submission checks exact string membership; valid hit gives +1 and removes entry.
- Uninstall removes `$HOME/Game`.

### `hide.py` (`HideGame`)
- SSH-check game with structured constraints.
- Install wipes and recreates `$HOME/Game`.
- Check executes a remote Bash script collecting metrics:
  - treasures count (`grep "^klad:"`)
  - total files, empty files
  - root-level treasures
  - root directory count
  - count of root dirs with required depth
- Validates metrics against settings and returns `required_user_score` on success.

### `test.py` (`TestGame`)
- Simple diagnostics game.
- Install writes `~/x.txt`.
- Uninstall removes file.
- `check` is intentionally unimplemented (`pass`), so it returns `None` in current code.

## SSH service (`backend/app/services/ssh.py`)
- `create_client(...)` creates Paramiko client with auto host key trust and shared timeout values.
- `create_client_from_config(ip)` binds credentials/timeouts from config.
- `execute_command(client, command)` returns decoded `(stdout, stderr)`.
- `check_ip(ip)` tries connect/close and returns bool.
- `upload_and_run_script(client, name, script)` writes `/tmp/{name}.sh`, chmod +x, executes via bash.

## JSON safety helper
`_json_safe_value` recursively converts:
- `dict` keys to strings
- tuples/sets to lists
- set order stabilized by sorting with `key=str`
Used before persisting game settings to avoid non-JSON-native payloads.

## Socket architecture

### Server (`backend/app/socket/server.py`)
- `AsyncServer(async_mode="asgi", transports websocket-compatible)`
- `ASGIApp(sio)` exported as `socket_app`

### Connection manager (`backend/app/socket/manager.py`)
- Two-way maps:
  - `_ip_to_sid`
  - `_sid_to_ip`
- Tracks current teacher IP (`_teacher_ip`, default `127.0.0.1`)
- Teacher identified by loopback IP on connect
- Provides event fanout helpers:
  - `send_to_ip`
  - `send_to_teacher`
  - `send_to_everyone`
  - `send_to_everyone_except_teacher`

### Event handlers (`backend/app/socket/handlers.py`)
- `connect`: resolves IP (supports debug header override), registers mapping
- `disconnect`: removes mapping and logs unknown SIDs

## HTTP and socket security/authorization model
- Role model is IP-based:
  - loopback IP = teacher
  - any other IP = student
- Teacher-only endpoints guarded by dependency injection
- CORS is globally permissive (`allow_origins=["*"]`)
- Socket and HTTP both support optional debug IP override header for local development/testing when enabled

## API summary
- `GET /ping`
- User:
  - `POST /user/register`
  - `GET /user/all`
  - `GET /user/me`
  - `DELETE /user/me`
  - `POST /user/kick/{ip}`
- Game:
  - `GET /game/`
  - `GET /game/list`
  - `POST /game/`
  - `POST /game/check`
  - `POST /game/start`
  - `POST /game/stop`
  - `GET /game/state`
- Realtime namespace mounted at `/socket.io`

## Testing
- Test configuration in `pyproject.toml`:
  - `testpaths = ["backend/tests"]`
  - `pythonpath = ["."]`
- Coverage focus:
  - state sanitization and JSON-safe conversion
  - user registration/kick/delete flows
  - dependency-based IP resolution
  - game routing state transitions
  - game service unit behaviors
  - SSH connectivity abstraction
- Socket integration helpers exist in `backend/tests/support.py` and fixtures in `conftest.py`.

## Known implementation notes
- Global lifecycle state machine is persisted but only transitions in game router/service paths.
- `start_game()` and `stop_game()` are tolerant to per-user SSH failures (log and continue).
- `check()` behavior differs by game mode:
  - string mode adds score delta
  - SSH mode overwrites score with game return value
- `TestGame.check` is a no-op placeholder in current implementation.
