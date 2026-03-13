from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "NORM_"}

    database_path: Path = Path("norm.db")
    host: str = "0.0.0.0"
    port: int = 8000
    config_path: Path = Path("norm.yaml")


settings = Settings()
