import logging
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

import requests
from tqdm import tqdm

from chatdoc_arxiv.path_manager import DIR_MODELS, create_directory
from chatdoc_arxiv.st_pages.utils import ReturnMessage


class Rack:
    """simple class to manage LLM models from hugging face with basic getter, delete and download methods."""

    def __init__(self) -> None:
        self.dir_models = DIR_MODELS
        create_directory(self.dir_models)

    def get_available_models(self) -> dict[str, str]:
        return {file_path.stem: str(file_path) for file_path in self.dir_models.glob("*.gguf")}

    def delete_model(self, model_name: str) -> ReturnMessage:
        file_to_remove = self.dir_models / model_name
        if not file_to_remove.exists():
            return ReturnMessage(logging.error, f"File to delete {file_to_remove} not found.")
        file_to_remove.unlink()
        return ReturnMessage(logging.info, f"File {file_to_remove} deleted")

    def download_new_model(self, repo_name: str, gguf_filename: str) -> ReturnMessage:
        repo_url = f"https://huggingface.co/{repo_name}"

        if int(requests.get(repo_url, timeout=60).status_code / 100) != 2:
            return ReturnMessage(logging.error, f"Repo url {repo_url} not found.")

        if not gguf_filename.endswith(".gguf"):
            return ReturnMessage(
                logging.error,
                f"Filename extension not valid. Expetedd '.gguf', passed {gguf_filename}",
            )

        file_url = repo_url + f"/resolve/main/{gguf_filename}"

        if gguf_filename.replace(".gguf", "") in set(self.get_available_models().keys()):
            return ReturnMessage(logging.info, "Selected model already downloaded")

        try:
            with tqdm(unit="B", unit_scale=True, miniters=1, desc="Download") as pbar:
                logging.info(f"Download for {file_url} submitted. It may take a while")
                urlretrieve(
                    file_url,
                    str(self.dir_models / gguf_filename),
                    reporthook=lambda _, b, total: pbar.update(b),
                )
                return ReturnMessage(logging.info, f"File {file_url} downloaded to folder {self.dir_models}")
        except (URLError, HTTPError) as e:
            return ReturnMessage(
                logging.error,
                (
                    f"Error downloading the file: {e}. "
                    f"If the problem persists, please download manually and move under {self.dir_models}"
                ),
            )
