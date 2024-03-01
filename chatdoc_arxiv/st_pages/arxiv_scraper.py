import logging

import pandas as pd
import st_aggrid as sta
import streamlit as st
from st_aggrid.shared import GridUpdateMode

from chatdoc_arxiv.scraparxiv.shelf import PAPER_COLUMNS, Shelf
from chatdoc_arxiv.st_pages.abc_page import AbcPage
from chatdoc_arxiv.st_pages.utils import Timer, build_grid_options


class Page(AbcPage):
    def __init__(self) -> None:
        self.shelf: Shelf = Shelf()

    @Timer("Page display - download and manage papers from arxiv", logging)
    def display(self):
        if "df_shelf" not in st.session_state:
            st.session_state["df_shelf"] = pd.DataFrame(columns=PAPER_COLUMNS)

        st.markdown("## Papers")

        with st.expander("Search for papers", expanded=True):
            col1_a, col2_a, col3_a = st.columns([2, 1, 1])
            selected_keywords = col1_a.text_input("Keywords")
            selected_start_index = col2_a.number_input("Start index", min_value=1, max_value=100, value=1)
            selected_max_results = col3_a.number_input("Max number of results", min_value=10, max_value=1_000, value=10)

            json_row_search = sta.AgGrid(
                st.session_state["df_shelf"],
                gridOptions=build_grid_options(st.session_state["df_shelf"], selection_mode="multiple"),
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
            )

            col1_b, col2_b, _ = st.columns([1, 1, 3])

            if col1_b.button("query"):
                self.shelf.query(
                    selected_keywords,
                    start_index=selected_start_index,
                    max_results=selected_max_results,
                )

                st.session_state["df_shelf"] = self.shelf.get_papers_info_df()
                st.rerun()

            if len(st.session_state["df_shelf"]) > 0 and len(json_row_search["selected_rows"]) > 0:
                if col2_b.button("Download selected"):
                    # self.shelf.download_papers(list_ids=list_selected)
                    list_selected = [
                        json_row_search["selected_rows"][j]["paper_id"]
                        for j in range(len(json_row_search["selected_rows"]))
                    ]
                    self.shelf.download_papers_from_list_ids(list_ids=list_selected)
                    st.write(f"downloading selected papers {list_selected}")
                    st.rerun()

        with st.expander("Downloaded papers", expanded=True):
            df_papers_already_downloaded = self.shelf.get_papers_info_already_downloaded_df()

            json_row_downloaded = sta.AgGrid(
                df_papers_already_downloaded,
                gridOptions=build_grid_options(df_papers_already_downloaded, selection_mode="multiple"),
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
            )
            list_downloaded_selected = [
                json_row_downloaded["selected_rows"][j]["paper_id"]
                for j in range(len(json_row_downloaded["selected_rows"]))
            ]
            if len(list_downloaded_selected) > 0:
                if st.button("Delete selected from download folder"):
                    self.shelf.delete_downloaded_paper_by_list_id(list_downloaded_selected)
                    st.rerun()

        logging.info("End of page")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    Page().display()
