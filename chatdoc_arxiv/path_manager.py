import logging
import sys
from pathlib import Path

DIR_REPO = Path(__file__).resolve().parent.parent

DIR_MODELS = DIR_REPO /  "models"
DIR_PAPERS = DIR_REPO /  "papers"
DIR_IMAGES = DIR_REPO /  "images"


def create_directory(directory: Path) -> None:
    """Create directory if it does not exist"""
    try:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created '{directory}' directory")
    except OSError as e:
        logging.exception(f"Error creating directory: {e}")
        sys.exit(1)
