import random

from backend.app.games import Game
from backend.app.games import GameSettingsItem
from pydantic import Field


class FindGame(Game):
    name: str = "Поиск кладов"
    description: str = "Найдите все 5 спрятанных кладов на машине. Клады - это строки в файлах, которые начинаются со слова \"klad:\". Ищите в папке Game в домашнем каталоге пользователя."

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
        )
    }
    default_game_data: dict = Field(default_factory=lambda: {
        "hidden_klads": set()
    })

    def install(self, client, game_data):
        root = "$HOME/Game"
        words = [t.rstrip() for t in open("words.txt").readlines()]
        treasures_amount = int(self.settings["treasures_amount"])
        files_amount = int(self.settings["files_amount"])

        if files_amount < treasures_amount:
            raise ValueError("files_amount must be greater than or equal to treasures_amount")

        # Generate directory structure
        mkname = lambda: "_".join(random.choice(words) for _ in range(2))

        dir_structure = []
        for i in range(5):
            dir1 = mkname()
            dir_structure.append(f"{root}/{dir1}")
            for j in range(5):
                dir2 = mkname()
                dir_structure.append(f"{root}/{dir1}/{dir2}")
                for k in range(5):
                    dir3 = mkname()
                    dir_structure.append(f"{root}/{dir1}/{dir2}/{dir3}")

        # Generate klad patterns
        klad_patterns = []
        for _ in range(treasures_amount):
            three_words = ' '.join(random.sample(words, 3))
            klad_patterns.append(f"klad:{three_words}")

        # Select directories for files
        selected_dirs = random.sample(dir_structure, files_amount)
        klad_dirs = selected_dirs[:treasures_amount]
        regular_dirs = selected_dirs[treasures_amount:]

        # Determine which files to gzip
        # Roughly half of treasure files are gzipped
        gzipped_treasures = min(treasures_amount // 2, treasures_amount)
        klad_gzip_flags = [True] * gzipped_treasures + [False] * (treasures_amount - gzipped_treasures)
        random.shuffle(klad_gzip_flags)

        # Regular files about 50% chance of getting gzipped
        regular_gzip_flags = [random.choice([True, False]) for _ in range(max(0, files_amount - treasures_amount))]

        # Build the script
        script_lines = [
            "#!/bin/bash",
            # "set -e",
            f"rm -rf \"{root}\"",
            f"mkdir \"{root}\"",
            ""
        ]

        # Add directory creation commands
        for dir_path in dir_structure:
            script_lines.append(f"mkdir -p \"{dir_path}\"")

        script_lines.extend(["", ""])

        # Add regular file creation commands
        for dir_path, should_gzip in zip(regular_dirs, regular_gzip_flags):
            filename = mkname() + ".txt"
            full_path = f"{dir_path}/{filename}"

            if should_gzip:
                script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
                for _ in range(20):
                    line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                    script_lines.append(line)
                script_lines.append("EOF")
                script_lines.append(f"gzip \"{full_path}\"")
            else:
                script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
                for _ in range(20):
                    line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                    script_lines.append(line)
                script_lines.append("EOF")

            script_lines.append("")

        # Add klad file creation commands
        for (dir_path, pattern), should_gzip in zip(zip(klad_dirs, klad_patterns), klad_gzip_flags):
            filename = mkname() + ".txt"
            full_path = f"{dir_path}/{filename}"

            if should_gzip:
                script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
                script_lines.append(pattern)
                for _ in range(19):
                    line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                    script_lines.append(line)
                script_lines.append("EOF")
                script_lines.append(f"gzip \"{full_path}\"")
            else:
                script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
                script_lines.append(pattern)
                for _ in range(19):
                    line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                    script_lines.append(line)
                script_lines.append("EOF")

            script_lines.append("")

        # Join script lines
        script_content = "\n".join(script_lines)

        # Write and execute script on remote
        script_path = "/tmp/create_structure.sh"

        client.exec_command(f'cat > {script_path} << \"SCRIPT_EOF\"\n{script_content}\nSCRIPT_EOF')
        client.exec_command(f"chmod +x {script_path}")
        stdin, stdout, stderr = client.exec_command(script_path)

        # Clean up
        client.exec_command(f"rm -f {script_path}")
        game_data["hidden_klads"] = set(klad_patterns)
        
    def check_string_submission(self, submission, game_data):
        if submission in game_data["hidden_klads"]:
            game_data["hidden_klads"].remove(submission)
            return 1
        return 0
    
    def uninstall(self, client, game_data):
        client.exec_command("rm -rf $HOME/Game")