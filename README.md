# SchoolLinux: Interactive Linux Terminal Training System

SchoolLinux backend supports plugin-like educational games.
Teachers can add new games by creating Python files in backend/app/games.

## Where To Write Games

- Put every custom game in backend/app/games/<your_game>.py.
- Do not modify backend internals for normal game creation.
- Import only the teacher-facing API:

```python
from backend.app.games import Game, GameSettingsItem
```

## Game Class Contract

Each game must inherit Game and implement methods below.

```python
class MyGame(Game):
	def install(self, client, game_data):
		...

	def check(self, client, game_data):
		...

	def uninstall(self, client, game_data):
		...
```

If your game expects text answers from user, set string_submission=True and implement:

```python
def check_string_submission(self, submission, game_data):
	...
```

## Teacher-Facing Fields

These fields are part of Game and should be defined in your class:

- name: game title shown in UI.
- description: task description for students.
- settings_form: declarative settings schema visible to teacher.
- settings: resolved settings values for this game instance (read-only reference in game logic).
- string_submission: True if game validates text answers.
- anticheat_required: True if anti-cheat should run.
- default_game_data: initial per-student runtime data template.
- required_user_score: score needed to complete this game.

## Settings Model

Define settings via settings_form using GameSettingsItem.
Supported item types:

- string
- number
- boolean
- option (requires options dict)

Example:

```python
settings_form = {
	"difficulty": GameSettingsItem(
		name="Difficulty",
		type="option",
		options={"easy": "Easy", "medium": "Medium", "hard": "Hard"},
		default="medium",
	),
	"folders": GameSettingsItem(
		name="Folders count",
		type="number",
		default=5,
	),
}
```

When settings are applied by backend, values are available in self.settings:

```python
difficulty = self.settings["difficulty"]
folders = int(self.settings["folders"])
```

## Runtime Game Data

Use default_game_data to declare per-student runtime storage shape.
Backend resets this structure for new game starts.

Example:

```python
default_game_data = {
	"hidden_klads": set(),
	"attempts": 0,
}
```

Inside methods, read and mutate game_data only for student progress:

```python
game_data["attempts"] += 1
```

## SSH Client Usage

install/check/uninstall receive connected paramiko SSH client.
Use it to create files, run shell commands, and verify answers on student machine.

Example:

```python
stdin, stdout, stderr = client.exec_command("ls -la $HOME/Game")
```

## Minimal Complete Example

```python
from backend.app.games import Game, GameSettingsItem


class EchoGame(Game):
	name = "Echo"
	description = "Student should create $HOME/Game/message.txt with expected text"
	string_submission = False
	anticheat_required = False
	required_user_score = 1

	settings_form = {
		"expected_text": GameSettingsItem(
			name="Expected text",
			type="string",
			default="hello",
		)
	}

	default_game_data = {
		"checked": False,
	}

	def install(self, client, game_data):
		client.exec_command("mkdir -p $HOME/Game")
		game_data["checked"] = False

	def check(self, client, game_data):
		expected = self.settings["expected_text"]
		stdin, stdout, stderr = client.exec_command("cat $HOME/Game/message.txt 2>/dev/null")
		content = stdout.read().decode().strip()
		if content == expected and not game_data["checked"]:
			game_data["checked"] = True
			return 1
		return 0

	def uninstall(self, client, game_data):
		client.exec_command("rm -rf $HOME/Game")

	def check_string_submission(self, submission, game_data):
		return 0
```

## Discovery Rules

- Backend auto-loads all .py files in backend/app/games.
- Files starting with underscore are ignored.
- Every class inheriting Game is discovered and instantiated.

## Best Practices For Teachers

- Keep game logic deterministic when possible.
- Validate settings assumptions in install.
- Store only progress data in game_data; use self.settings for configuration.
- Always clean up created files in uninstall.
- Keep descriptions explicit so students know success criteria.

## Release Tarball CI

- CI workflow `.github/workflows/release-tarball.yml` runs on every pushed tag.
- It builds frontend, runs backend tests, and creates `SchoolLinux-<tag>.tar.gz`.
- The tarball contains:
	- `backend/`
	- `frontend/dist/`
	- `.env` (copied from `.env.example`)
	- `requirements.txt`
	- `install.sh`
	- `run.sh`

After extracting a release tarball:

```bash
./install.sh
./run.sh
```
