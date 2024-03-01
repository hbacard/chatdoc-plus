"""Pages launcher."""

import logging

import streamlit as st
from path_manager import DIR_IMAGES
from PIL import Image

from chatdoc_arxiv.st_pages import arxiv_scraper, chatdoc, download_llm_models

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---

st.set_page_config(
    layout="wide",  # Can be "centered" or "wide".
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    page_title="Chatdoc ArXiv",
    page_icon=str(DIR_IMAGES / "llama_ai.png"),  # favicon
)

# ---

PAGES = {
    " 🔂 LLM Models": download_llm_models.Page().display,
    " 📖 Papers": arxiv_scraper.Page().display,
    " 💬 Chatdoc": chatdoc.Page().display,
}


if __name__ == "__main__":
    with st.sidebar:
        st.title("ChatDoc ArXiv")
        st.image(Image.open(DIR_IMAGES / "llama_ai.png"), use_column_width=False)

    mode = st.sidebar.selectbox(" ", list(PAGES.keys()))
    PAGES[mode]()
