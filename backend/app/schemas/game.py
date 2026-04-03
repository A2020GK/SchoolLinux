from . import BaseSchema
from typing import Literal
from pydantic import Field

class GameConfig(BaseSchema):
    directory_depth: int = 3
    files_total: int = 5
    gzipped_files: int = 0
    treasure_files: int = 5
    gzipped_treasure_files: int = 0
        

type GameType = Literal["find", "hide"]

class Game(BaseSchema):
    type: GameType = "find"
    active: bool = False
    config: GameConfig = Field(default_factory=GameConfig)
    
class GameTask(BaseSchema):
    pass

class GameTaskFind(GameTask):
    treasures: set[str] = set()
    
class GameTaskHide(GameTask):
    criteria_matches: bool = False