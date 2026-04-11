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
    
    ssh_user: str = "game"
    ssh_password: str = "game"
    ssh_timeout: float = Field(default=10.0)
    allow_ip_override: bool = Field(default=False)
    ip_override_header: str = Field(default="X-Debug-IP")
    
config = Config()