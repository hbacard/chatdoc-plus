import logging
import time

import pandas as pd
import st_aggrid as sta
import streamlit as st
from st_aggrid.shared import GridUpdateMode

from chatdoc_arxiv.scrapmodels.rack import Rack
from chatdoc_arxiv.st_pages.abc_page import AbcPage
from chatdoc_arxiv.st_pages.utils import Timer, build_grid_options


class Page(AbcPage):
    def __init__(self) -> None:
        self.rack: Rack = Rack()

    @Timer("Page display - download and manage llm models", logging)
    def display(self):
        spinner_placeholder = st.empty()
        st.markdown("## Models")

        with st.expander("Available models", expanded=True):
            dict_available_models = self.rack.get_available_models()
            df_models = pd.DataFrame(
                {"model name": dict_available_models.keys(), "path": dict_available_models.values()}
            )

            json_row = sta.AgGrid(
                df_models,
                gridOptions=build_grid_options(df_models, selection_mode="single"),
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
            )
            if len(df_models) > 0:
                if st.button("delete"):
                    if len(json_row["selected_rows"]) == 0:
                        st.info("Please select one row to delete.")
                        return
                    selected_model_name = json_row["selected_rows"][0]["model name"]
                    self.rack.delete_model(selected_model_name + ".gguf")
                    time.sleep(1)
                    logging.info(f"Model {selected_model_name} deleted")
                    st.rerun()
            else:
                st.info("No models downloaded yet")

        # download new models
        with st.expander("Download a model (it may take a while)", expanded=True):
            col1, col2 = st.columns([1, 1])
            selected_repo = col1.text_input("Hugging face repository", value="mlabonne/NeuralBeagle14-7B-GGUF")
            selected_model = col2.text_input("guff filename (with extension)", value="neuralbeagle14-7b.Q5_K_M.gguf")
            if st.button("Download"):
                with spinner_placeholder:
                    with st.spinner("Downloading model"):
                        msg = self.rack.download_new_model(selected_repo, selected_model)
                msg.logging_streamlit(msg.message)

        logging.info("End of page")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    Page().display()
