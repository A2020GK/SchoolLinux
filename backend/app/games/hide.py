from backend.app.games import Game, GameSettingsItem

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
        # TODO: Install Game folder on machine
        pass
    
    def check(self, client, game_data):
        # TODO: Check if the student has hidden the klads correctly and update the score        
        pass
    
    def uninstall(self, client, game_data):
        # TODO: Delete Game folder from machine
        pass
    
