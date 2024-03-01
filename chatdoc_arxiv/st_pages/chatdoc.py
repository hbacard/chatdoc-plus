import logging
import os

import st_aggrid as sta
import streamlit as st
from langchain_community.llms import LlamaCpp
from llama_index import GPTVectorStoreIndex, ServiceContext, SimpleDirectoryReader
from st_aggrid.shared import GridUpdateMode

from chatdoc_arxiv.path_manager import DIR_MODELS, DIR_PAPERS
from chatdoc_arxiv.scraparxiv.shelf import Shelf
from chatdoc_arxiv.scrapmodels.rack import Rack
from chatdoc_arxiv.st_pages.abc_page import AbcPage
from chatdoc_arxiv.st_pages.utils import Timer, build_grid_options

qa_prompt_template = """{system_prompt}.\n
### Instruction:{query}
### Response :

"""

system_prompt = (
    "You are a very helpful assistant. Perform the following instructions to the best of your ability ."
    "You always give your answers in English with a good writing style.\n"
)


class Page(AbcPage):
    def __init__(self) -> None:
        self.shelf: Shelf = Shelf()
        self.rack: Rack = Rack()
        self.llm_instance: LlamaCpp | None = None

    @staticmethod
    def set_llm(selected_model, n_ctx: int = 4096, temperature: float = 0.0, max_tokens: int = 2048):
        return LlamaCpp(
            model_path=str(DIR_MODELS / (selected_model + ".gguf")),
            n_batch=512,
            n_gpu_layers=2,
            f16_kv=True,
            verbose=True,
            n_ctx=n_ctx,  # Max 4096
            top_k=10,
            top_p=0.95,
            repeat_penalty=1.1,
            temperature=temperature,
            seed=42,
            max_tokens=max_tokens,  # Can be smaller
        )

    def get_model_response(self, query, file_path_paper=None):
        if file_path_paper is None:
            logging.info("SPAM: before query")
            prompt = qa_prompt_template.format(system_prompt=system_prompt, query=query)
            answer = self.llm_instance(prompt=prompt)
            logging.info("SPAM: after query")
        else:
            if not os.path.exists(file_path_paper):
                return f"Not a valid file: {file_path_paper}"

            context_window, num_output, chunk_overlap = 2048, 1024, 20
            documents = (
                SimpleDirectoryReader(input_files=[file_path_paper]).load_data()
                if os.path.isfile(file_path_paper)
                else SimpleDirectoryReader(file_path_paper).load_data()
            )
            service_context = ServiceContext.from_defaults(
                llm=self.llm_instance,
                system_prompt=system_prompt,
                context_window=context_window,
                chunk_overlap=chunk_overlap,
                num_output=num_output,
                embed_model="local",
            )
            index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
            answer = index.as_query_engine().query(query)
        return answer or "Oops! No result found"

    @Timer("Page display - run selected model with the selected paper", logging)
    def display(self):
        path_to_paper = None

        with st.sidebar:
            st.markdown("Models selector")
            available_models = self.rack.get_available_models()
            if len(available_models) == 0:
                st.info("Please download a model via 'Download' page")
            else:
                selected_model = st.selectbox("Selected models", self.rack.get_available_models())
                n_ctx = st.selectbox("n_ctx", [4096, 2048, 1024, 512, 256])
                max_tokens = st.selectbox("max_tokens", [2048, 1024, 512, 256])
                self.llm_instance = self.set_llm(selected_model, n_ctx, max_tokens)
                st.info(f"Model: {selected_model} - {n_ctx} - {max_tokens} instantiated")

        with st.expander("Papers selector", expanded=True):
            df_papers_already_downloaded = self.shelf.get_papers_info_already_downloaded_df()

            json_row_downloaded = sta.AgGrid(
                df_papers_already_downloaded,
                gridOptions=build_grid_options(df_papers_already_downloaded, selection_mode="single"),
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
            )
            selected_paper_id = None
            if len(json_row_downloaded["selected_rows"]) > 0:
                selected_paper_id = json_row_downloaded["selected_rows"][0]["paper_id"]
                path_to_paper = str(DIR_PAPERS / (selected_paper_id + ".pdf"))
                selected_title = df_papers_already_downloaded.loc[
                    df_papers_already_downloaded["paper_id"] == selected_paper_id, "title"
                ].iloc[0]
                st.write(f"Selected paper: '{selected_title}'")

        if path_to_paper:
            query_prompt = "What would you like to ask about this document?"
        else:
            query_prompt = "Ask any question, or select a paper in the table."

        if "query_submitted" not in st.session_state:
            st.session_state["query_submitted"] = False

        query = st.chat_input(placeholder=query_prompt)

        if query is not None:
            st.session_state["query_submitted"] = True

        if st.session_state["query_submitted"] and query:
            with st.chat_message(name="Q"):
                st.write(query)
            try:
                answer = self.get_model_response(query, path_to_paper)
                with st.chat_message(name="A"):
                    st.success(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")

        logging.info("End of page")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    Page().display()
