from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from pydantic import Field

from backend.app.games import Game, GameSettingsItem, execute_command, upload_and_run_script


WORDS_PATH = Path(__file__).with_name("words.txt")
SCRIPT_NAME = "find_game_install"


class FindGame(Game):
    name: str = "Поиск кладов"
    description: str = (
        "Найдите все спрятанные клады на машине. Клады - это строки в файлах, "
        "которые начинаются со слова \"klad:\". Ищите в папке Game в домашнем каталоге пользователя."
    )

    string_submission: bool = True
    anticheat_required: bool = True
    required_user_score: int = 5
    settings_form: dict[str, GameSettingsItem] = {
        "treasures_amount": GameSettingsItem(
            name="Количество кладов",
            type="number",
            default=5
        ),
        "files_amount": GameSettingsItem(
            name="Количество файлов с содержимым",
            type="number",
            default=30
        ),
        "max_depth": GameSettingsItem(
            name="Максимальная глубина дерева папок",
            type="number",
            default=3
        ),
        "content_lines": GameSettingsItem(
            name="Количество строк в каждом файле",
            type="number",
            default=20
        ),
        "gzip_percent": GameSettingsItem(
            name="Процент файлов в формате .gz",
            type="number",
            default=40
        )
    }
    default_game_data: dict = Field(default_factory=lambda: {
        "hidden_klads": set()
    })

    def apply_settings(self, settings: dict[str, Any] | None = None) -> None:
        super().apply_settings(settings)
        self.required_user_score = max(1, int(self.settings["treasures_amount"]))

    def _load_words(self) -> list[str]:
        if not WORDS_PATH.exists():
            raise ValueError(f"Words dictionary is missing: {WORDS_PATH}")

        return [line.strip().lower() for line in WORDS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]

    @staticmethod
    def _mkname(words: list[str]) -> str:
        return "_".join(random.choice(words) for _ in range(2))

    @staticmethod
    def _mkline(words: list[str]) -> str:
        return " ".join(random.choices(words, k=random.randint(3, 8)))

    @staticmethod
    def _normalize_submission(submission: str) -> str:
        compact = " ".join(str(submission).strip().split())
        if not compact:
            return ""

        prefix, separator, tail = compact.partition(":")
        if separator and prefix.strip().lower() == "klad":
            normalized_tail = " ".join(tail.strip().split()).lower()
            return f"klad:{normalized_tail}"

        return compact.lower()

    @staticmethod
    def _normalize_hidden_klads(game_data: dict[str, Any]) -> set[str]:
        raw_hidden = game_data.get("hidden_klads", set())

        if isinstance(raw_hidden, set):
            normalized = {str(item) for item in raw_hidden}
        elif isinstance(raw_hidden, (list, tuple)):
            normalized = {str(item) for item in raw_hidden}
        else:
            normalized = set()

        game_data["hidden_klads"] = normalized
        return normalized

    def _generate_treasure_patterns(self, words: list[str], treasures_amount: int) -> list[str]:
        patterns: set[str] = set()

        while len(patterns) < treasures_amount:
            three_words = " ".join(random.sample(words, 3))
            patterns.add(f"klad:{three_words}")

        return list(patterns)

    def install(self, client, game_data):
        treasures_amount = max(1, int(self.settings["treasures_amount"]))
        files_amount = max(treasures_amount, int(self.settings["files_amount"]))
        max_depth = max(1, int(self.settings["max_depth"]))
        content_lines = max(2, int(self.settings["content_lines"]))
        gzip_percent = max(0, min(100, int(self.settings["gzip_percent"])))
        self.required_user_score = treasures_amount

        words = self._load_words()
        klad_patterns = self._generate_treasure_patterns(words, treasures_amount)

        treasure_positions = set(random.sample(range(files_amount), treasures_amount))
        shuffled_klads = random.sample(klad_patterns, len(klad_patterns))
        next_klad_idx = 0

        files: list[dict[str, Any]] = []
        used_paths: set[str] = set()

        while len(files) < files_amount:
            depth = random.randint(1, max_depth)
            dirs = [self._mkname(words) for _ in range(depth)]
            filename = f"{self._mkname(words)}.txt"
            rel_path = "/".join(dirs + [filename])

            if rel_path in used_paths:
                continue

            used_paths.add(rel_path)

            is_treasure_file = len(files) in treasure_positions
            treasure_line = None

            if is_treasure_file:
                treasure_line = shuffled_klads[next_klad_idx]
                next_klad_idx += 1

            lines: list[str] = []
            if treasure_line is not None:
                lines.append(treasure_line)
                for _ in range(content_lines - 1):
                    lines.append(self._mkline(words))
            else:
                for _ in range(content_lines):
                    lines.append(self._mkline(words))

            should_gzip = random.randint(1, 100) <= gzip_percent

            files.append(
                {
                    "rel_path": rel_path,
                    "lines": lines,
                    "is_treasure": is_treasure_file,
                    "gzip": should_gzip,
                }
            )

        treasure_file_indexes = [idx for idx, item in enumerate(files) if item["is_treasure"]]
        if treasure_file_indexes and all(files[idx]["gzip"] for idx in treasure_file_indexes):
            files[random.choice(treasure_file_indexes)]["gzip"] = False

        script_lines = [
            "#!/bin/bash",
            "set -euo pipefail",
            "ROOT=\"$HOME/Game\"",
            "rm -rf \"$ROOT\"",
            "mkdir -p \"$ROOT\"",
            ""
        ]

        for file_meta in files:
            rel_path = file_meta["rel_path"]
            rel_dir = rel_path.rsplit("/", 1)[0]

            script_lines.append(f"mkdir -p \"$ROOT/{rel_dir}\"")
            script_lines.append(f"cat > \"$ROOT/{rel_path}\" << 'EOF_FIND'")
            script_lines.extend(file_meta["lines"])
            script_lines.append("EOF_FIND")

            if file_meta["gzip"]:
                script_lines.append(f"gzip -f \"$ROOT/{rel_path}\"")

            script_lines.append("")

        script_content = "\n".join(script_lines)
        upload_and_run_script(client, SCRIPT_NAME, script_content)

        game_data["hidden_klads"] = set(klad_patterns)
        pass
    def check_string_submission(self, submission, game_data):
        hidden_klads = self._normalize_hidden_klads(game_data)
        normalized_submission = self._normalize_submission(submission)

        if normalized_submission in hidden_klads:
            hidden_klads.remove(normalized_submission)
            return 1

        return 0

    def uninstall(self, client, game_data):
        execute_command(client, 'rm -rf "$HOME/Game"')