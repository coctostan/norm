import logging
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = {"env_prefix": "NORM_"}

    database_path: Path = Path("norm.db")
    host: str = "0.0.0.0"
    port: int = 8000
    config_path: Path = Path("norm.yaml")
    watch_debounce_ms: int = 1000


settings = Settings()


def load_config() -> list[dict]:
    """Read norm.yaml and return the projects list.

    Each project dict has 'name' and 'path' keys.
    Returns empty list if file doesn't exist or has no projects.
    """
    config_file = Path(settings.config_path)
    if not config_file.exists():
        return []

    with open(config_file) as f:
        data = yaml.safe_load(f)

    if not data or not isinstance(data.get("projects"), list):
        return []

    return [p for p in data["projects"] if isinstance(p, dict) and "name" in p and "path" in p]


def save_config(projects: list[dict]) -> None:
    """Write the current projects list to norm.yaml.

    Preserves settings section from existing file.
    """
    config_file = Path(settings.config_path)

    # Load existing data to preserve settings section
    existing = {}
    if config_file.exists():
        with open(config_file) as f:
            existing = yaml.safe_load(f) or {}

    existing["projects"] = [{"name": p["name"], "path": p["path"]} for p in projects]

    with open(config_file, "w") as f:
        yaml.dump(existing, f, default_flow_style=False, sort_keys=False)
