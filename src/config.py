import os
import sys
from pathlib import Path


def setup_directories(app_dir: Path) -> dict[str, Path]:
    QUEUE_DIR = "queue"
    FAILURES_DIR = "failures"
    COMPLETE_DIR = "complete"

    directories = {
        "QUEUE_DIR": app_dir / QUEUE_DIR,
        "FAILURES_DIR": app_dir / FAILURES_DIR,
        "COMPLETE_DIR": app_dir / COMPLETE_DIR,
    }

    for dir_path in directories.values():
        dir_path.mkdir(exist_ok=True)
    return directories


class Config:
    APP_DIR: Path = Path().resolve()
    STATIC_DIR: Path = APP_DIR / "static"

    directories: dict = setup_directories(APP_DIR)

    API_HOST: str = "api.crossref.org"
    EMAIL_ADDRESS: str = os.environ.get("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD", "")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
        sys.exit(1)

    HEADERS: dict = {
        "Content-type": "application/json",
        "User-Agent": f"dopi mailto:{EMAIL_ADDRESS}",
        "Mailto": EMAIL_ADDRESS,
    }

    LOCK_FILE: str = "doi_processing.lock"
    LOCK_FILEPATH: Path = APP_DIR / LOCK_FILE

    """ Bottle server config """
    HOST: str = os.environ.get("HOST", "localhost")
    PORT: int = int(os.environ.get("PORT", 8080))
    DEBUG: bool = os.environ.get("DEBUG", "True").lower() == "true"
