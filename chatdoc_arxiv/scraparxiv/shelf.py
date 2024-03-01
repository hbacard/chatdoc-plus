import concurrent.futures
import glob
import logging
import os
import urllib.request
from collections import OrderedDict

import pandas as pd
import requests
import xmltodict
from path_manager import DIR_PAPERS, create_directory

from chatdoc_arxiv.st_pages.utils import ReturnMessage

PAPER_COLUMNS = [
    "paper_id",
    "title",
    "date",
    "authors",
]


def parse_authors_and_affiliation(authors: dict) -> list:
    names_affiliations = []
    if isinstance(authors, list):
        for au in authors:
            name = au.get("name")
            try:
                affiliation = au.get("arxiv:affiliation").get("#text")
            except:
                affiliation = ""
            names_affiliations.append((name, affiliation))

    else:
        name = authors.get("name")
        try:
            affiliation = au.get("arxiv:affiliation").get("#text")
        except:
            affiliation = ""
        names_affiliations.append((name, affiliation))

    return names_affiliations


class Shelf:
    def __init__(self):
        """Shelf data structure where the queried results are stored.
        The paper in the virtual shelf can be downloaded to a local folder.
        """
        self.papers: OrderedDict | None = None
        self.dir_papers = DIR_PAPERS
        create_directory(self.dir_papers)

    @staticmethod
    def _download_a_paper(paper_url, path_destination) -> ReturnMessage:
        try:
            with urllib.request.urlopen(paper_url, timeout=60) as conn:
                urllib.request.urlretrieve(paper_url, path_destination)
                ReturnMessage(logging.info, f"Download paper {paper_url} finished.")
                return len(conn.read())  # number of bytes in downloaded image

        except urllib.error.HTTPError:
            logging.error(f"Http can not retrieve the paper {paper_url}")
        except Exception as e:
            logging.error(e)

    @staticmethod
    def _parse_feed(feed: OrderedDict) -> dict:
        output_info = dict()

        entries = feed.get("feed").get("entry")
        if entries is None:
            logging.info("No entries found")
            return None
        if not isinstance(entries, list):
            # there is a single paper in the query
            entries = [entries]

        for entry in entries:
            paper_id = entry.get("id").split("/")[-1]
            paper_title = entry.get("title").replace("\n", "").replace("  ", "").strip()
            paper_published_date = entry.get("published")
            authors = [a[0] for a in parse_authors_and_affiliation(entry.get("author"))]

            output_info.update(
                {
                    paper_id: {
                        "title": paper_title,
                        "date": paper_published_date,
                        "authors": authors,
                    },
                },
            )
        return output_info

    def query(self, keywords=None, start_index=1, max_results=10) -> ReturnMessage:
        """Main method of the class, to fill the virtual shelf with papers.
        Fill the shelf with papers form arxiv API, with given keyword, index and max number of papers found.
        To see the output type self.papers.
        """
        keywords = ":" + keywords if keywords else ""
        a_url = f"http://export.arxiv.org/api/query?search_query=all{keywords}&start={start_index}&max_results={max_results}"
        r = requests.get(a_url, timeout=120)
        if int(r.status_code / 100) != 2:
            return ReturnMessage(logging.error, f"Error {r.status_code} parsing data from url {a_url}")
        dd = xmltodict.parse(r.content)
        self.papers = dd
        return ReturnMessage(logging.info, "Query completed")

    def get_papers_info(self) -> dict:
        """Get info from the paper in the Shelf.papers into a dict"""
        return self._parse_feed(self.papers)

    def get_papers_info_df(self) -> pd.DataFrame:
        if len(self.get_papers_info()):
            return pd.DataFrame(self.get_papers_info()).T.reset_index().rename(columns={"index": "paper_id"})
        else:
            return pd.DataFrame(columns=PAPER_COLUMNS)

    def get_list_id_papers_already_downloaded(self):
        return [
            os.path.basename(file).replace(".pdf", "") for file in glob.glob(os.path.join(self.dir_papers, "*.pdf"))
        ]

    def download_papers_from_list_ids(self, list_ids: list[str]) -> ReturnMessage:
        """
        Idempotent function to download the data from the Shelf to the designated local folder
        If list_ids is None, then all the papers in the shelf are downloaded.
        Input ids can be any id and not necessarily in self.papers.
        """
        ids_already_downloaded = self.get_list_id_papers_already_downloaded()

        ids_to_download = set(list_ids) - set(ids_already_downloaded)

        list_urls = [f"http://arxiv.org/pdf/{i}.pdf" for i in ids_to_download]
        list_paths_destination = [os.path.join(self.dir_papers, os.path.basename(url)) for url in list_urls]

        logging.info("Downloading papers (in multi-threading...)")

        total_bytes = 0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._download_a_paper, url, dest)
                for url, dest in zip(list_urls, list_paths_destination, strict=False)
            ]
            for f in concurrent.futures.as_completed(futures):
                total_bytes += f.result() or 0

        logging.info(f"Approx total bytes downloaded {total_bytes}")
        return ReturnMessage(logging.info, f"Papers {list_ids} downloaded.")

    def get_paper_info_from_list_id(self, list_ids: list[str]) -> dict:
        a_url = f"http://export.arxiv.org/api/query?id_list={','.join(list_ids)}"
        r = requests.get(a_url, timeout=120)
        if int(r.status_code / 100) != 2:
            return ReturnMessage(logging.error, f"Error {r.status_code} parsing data from url {a_url}")
        dd = xmltodict.parse(r.content)
        return self._parse_feed(dd)

    def get_paper_info_from_list_id_df(self, list_ids: list[str]) -> dict:
        return (
            pd.DataFrame(self.get_paper_info_from_list_id(list_ids))
            .T.reset_index()
            .rename(columns={"index": "paper_id"})
        )

    def get_papers_info_already_downloaded(self):
        ids_already_downloaded = self.get_list_id_papers_already_downloaded()
        return self.get_paper_info_from_list_id(ids_already_downloaded)

    def get_papers_info_already_downloaded_df(self) -> pd.DataFrame:
        return (
            pd.DataFrame(self.get_papers_info_already_downloaded())
            .T.reset_index()
            .rename(columns={"index": "paper_id"})
        )

    def delete_downloaded_paper_by_list_id(self, list_ids) -> None:
        ids_already_downloaded = self.get_list_id_papers_already_downloaded()
        for idx in list_ids:
            if idx in ids_already_downloaded:
                os.remove(os.path.join(self.dir_papers, f"{idx}.pdf"))
                logging.info(f"Paper {idx} deleted.")
            else:
                logging.error(f"Can not delete {idx} as not downloaded.")

    def clean_download_directory(self) -> None:
        """Delete all the downloaded files in the destination folder"""
        files = glob.glob(os.path.join(self.dir_papers, "*.pdf"))
        for f in files:
            os.remove(f)
