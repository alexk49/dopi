import os
from pathlib import Path


def setup_directories(app_dir):
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
    APP_DIR = Path().resolve()
    STATIC_DIR = APP_DIR / "src" / "static"

    directories = setup_directories(APP_DIR)
    
    API_HOST = "api.crossref.org"
    EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")

    HEADERS = {
        "Content-type": "application/json",
        "User-Agent": f"dopi mailto:{EMAIL_ADDRESS}",
        "Mailto": EMAIL_ADDRESS,
    }
    
    LOCK_FILE = "doi_processing.lock"
    
    """ Bottle server config """
    HOST = os.environ.get("HOST", "localhost")
    PORT = int(os.environ.get("PORT", 8080))
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
