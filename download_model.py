import os
import sys
import argparse
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError
from tqdm import tqdm  # pip install tqdm for progress bar
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def parse_args():
    parser = argparse.ArgumentParser(description='Download a model file from Hugging Face.')
    parser.add_argument('--repo', default='mlabonne/NeuralBeagle14-7B-GGUF', help='Hugging Face repository name')
    parser.add_argument('--file', default='neuralbeagle14-7b.Q5_K_M.gguf', help='File name to download')
    return parser.parse_args()

def create_directory(directory: Path) -> None:
    """ Create directory if it does not exist """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created '{directory}' directory")
    except OSError as e:
        logging.error(f"Error creating directory: {e}")
        sys.exit(1)

def download_file(url: str, local_path: Path) -> None:
    """ Download file with a progress bar """
    try:
        with tqdm(unit='B', unit_scale=True, miniters=1, desc="Download") as pbar:
            urlretrieve(url, str(local_path), reporthook=lambda _, b, total: pbar.update(b))
    except (URLError, HTTPError) as e:
        logging.error(f"Error downloading the file: {e}")
        sys.exit(1)

def main():
    args = parse_args()
    HUGGINGFACE_REPO_NAME = args.repo
    GGUF_FILE_NAME = args.file

    MODELS_DIR = "models"
    URL = f"https://huggingface.co/{HUGGINGFACE_REPO_NAME}/resolve/main/{GGUF_FILE_NAME}"

    script_dir = Path(__file__).resolve().parent
    models_path = script_dir / MODELS_DIR
    local_path = models_path / GGUF_FILE_NAME

    create_directory(models_path)

    if not local_path.exists():
        logging.info("Downloading file...")
        download_file(URL, local_path)
    else:
        logging.info("File already exists, skipping download.")

if __name__ == "__main__":
    main()
