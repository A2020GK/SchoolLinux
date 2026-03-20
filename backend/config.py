from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Config(BaseSettings):
    """
    Application settings.
    Priority: Env vars -> .env file -> default values
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )
    debug: bool = True
    database_url: str = "sqlite:///./data.db"
    ssh_user: str = "game"
    ssh_password: str = "game"
    
config = Config()