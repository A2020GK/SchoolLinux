from backend.app.games import Game, GameSettingsItem, execute_command, upload_and_run_script

class HideGame(Game):
    name:str = "Прятание кладов"
    description:str = "Ученики прячут клады в соответствии с заданием"
    
    string_submission: bool = False
    anticheat_required: bool = True
    required_user_score: int = 10
    
    settings_form: dict[str, GameSettingsItem] = {
        "treasures_amount": GameSettingsItem(
            name="Целевое количество кладов",
            type="number",
            default=1
        ),
        "stubs": GameSettingsItem(
            name="Минимальное количество файлов, которые не являются кладом",
            type="number",
            default=3  
        ),
        "allow_empty_stubs": GameSettingsItem(
            name="Разрешить пустые файлы-заглушки",
            type="boolean",
            default=False
        ),
        "allow_root_treasures": GameSettingsItem(
            name="Разрешить клады в корневой папке Game",
            type="boolean",
            default=False
        ),
        "root_folders": GameSettingsItem(
            name="Количество папок в корневой папке Game",
            type="number",
            default=5
        ),
        "depth_folders": GameSettingsItem(
            name="Количество папок, которые должны содержать минимум уровней в глубину",
            type="number",
            default=1
        ),
        "depth": GameSettingsItem(
            name="Минимальный размер файлового дерева (в глубину) для выбранного количества папок",
            type="number",
            default=3
        ),
        
    }
    
    def install(self, client, game_data):
        script = f"""#!/bin/bash
    set -e
    rm -rf \"$HOME/Game\"
    mkdir -p \"$HOME/Game\"
    """

        upload_and_run_script(client, "hide_game_install", script)
        game_data["completed"] = False
    
    def check(self, client, game_data):
        if game_data.get("completed"):
            return self.required_user_score

        treasures_amount = int(self.settings["treasures_amount"])
        stubs_amount = int(self.settings["stubs"])
        allow_empty_stubs = bool(self.settings["allow_empty_stubs"])
        allow_root_treasures = bool(self.settings["allow_root_treasures"])
        root_folders = int(self.settings["root_folders"])
        depth_folders = int(self.settings["depth_folders"])
        depth = int(self.settings["depth"])

        command = f"""bash -lc '
ROOT=\"$HOME/Game\"
if [ ! -d \"$ROOT\" ]; then
  echo "treasures=0"
  echo "files=0"
  echo "empty_files=0"
  echo "root_treasures=0"
  echo "root_dirs=0"
  echo "deep_root_dirs=0"
  exit 0
fi

treasures=$(grep -Rsl "^klad:" "$ROOT" 2>/dev/null | wc -l)
files=$(find "$ROOT" -type f | wc -l)
empty_files=$(find "$ROOT" -type f -empty | wc -l)
root_treasures=$(find "$ROOT" -maxdepth 1 -type f -exec grep -q "^klad:" {{}} \; -print 2>/dev/null | wc -l)
root_dirs=$(find "$ROOT" -mindepth 1 -maxdepth 1 -type d | wc -l)
deep_root_dirs=$(find "$ROOT" -mindepth {depth} -type d 2>/dev/null | sed -E "s#^$ROOT/([^/]+).*#\\1#" | sort -u | wc -l)

echo "treasures=$treasures"
echo "files=$files"
echo "empty_files=$empty_files"
echo "root_treasures=$root_treasures"
echo "root_dirs=$root_dirs"
echo "deep_root_dirs=$deep_root_dirs"
'"""

        stdout, _ = execute_command(client, command)
        metrics: dict[str, int] = {}
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not value.isdigit():
                continue
            metrics[key] = int(value)

        treasures = metrics.get("treasures", 0)
        files = metrics.get("files", 0)
        empty_files = metrics.get("empty_files", 0)
        root_treasures = metrics.get("root_treasures", 0)
        root_dirs = metrics.get("root_dirs", 0)
        deep_root_dirs = metrics.get("deep_root_dirs", 0)
        stubs = max(0, files - treasures)

        if treasures != treasures_amount:
            return 0
        if stubs < stubs_amount:
            return 0
        if not allow_empty_stubs and empty_files > 0:
            return 0
        if not allow_root_treasures and root_treasures > 0:
            return 0
        if root_dirs != root_folders:
            return 0
        if deep_root_dirs < depth_folders:
            return 0

        game_data["completed"] = True
        return self.required_user_score
    
    def uninstall(self, client, game_data):
        execute_command(client, 'rm -rf "$HOME/Game"')
    
