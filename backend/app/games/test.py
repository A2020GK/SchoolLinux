from backend.app.games import Game, GameSettingsItem, execute_command, upload_and_run_script

class TestGame(Game):
    name:str = "Тестовая игра"
    description:str = "Игра для тестирования механики и отладки. Ничего не делает."
    
    string_submission: bool = False
    anticheat_required: bool = False
    required_user_score: int = 0
    
    settings_form: dict[str, GameSettingsItem] = {
        "test_setting": GameSettingsItem(
            name="Тестовая настройка",
            type="number",
            default=42
        )
    }
    
    def install(self, client, game_data):
        upload_and_run_script(client, "test", """
           #!/bin/bash
           
           echo "This is a test game. It does nothing." > ~/x.txt                   
        """)
    
    def check(self, client, game_data):
        pass
    
    def uninstall(self, client, game_data):
        execute_command(client, "rm -f ~/x.txt")