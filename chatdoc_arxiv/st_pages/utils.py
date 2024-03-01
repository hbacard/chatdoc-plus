"""The utils module no programmer would want to see, containing recurring functions across pages."""

import logging
from collections import defaultdict
from contextlib import ContextDecorator
from time import perf_counter as time

import pandas as pd
import streamlit as st
from st_aggrid.grid_options_builder import GridOptionsBuilder

LOGGING_DICT = {
    logging.info: st.info,
    logging.error: st.error,
    logging.warning: st.warning,
}


class ReturnMessage:
    """
    Class to communicate the error to front end while also rasing it to the log on one go
    Messenger design pattern
    """

    def __init__(self, logging_function, message) -> None:
        self.message: str = message
        self.logging_function: object = logging_function
        self.logging_streamlit = LOGGING_DICT[self.logging_function]
        # trigger the log when the method is instantiated
        self.logging_function(self.message)


class Timer(ContextDecorator):
    def __init__(self, message: str, logger: logging.Logger):
        self.message = message
        self.logger = logger

    def __enter__(self):
        self.start = time()
        self.logger.info(f"--> {self.message}: start ")

    def __exit__(self, *args):
        self.end = time()
        self.logger.info(f"--| {self.message}: end in {time() - self.start:.4f} seconds")


def build_grid_options(
    df: pd.DataFrame,
    selection_mode: str,
) -> defaultdict:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_default_column(
        groupable=True,
        value=True,
        enable_row_group=True,
        aggFunc="sum",
        editable=False,
        headerCheckboxSelection=None,
    )
    if len(df) > 0:
        gb.configure_selection(
            selection_mode=selection_mode,
            use_checkbox=True,
            pre_selected_rows=[],
        )
    gb.configure_grid_options(autoSizePadding=0)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    grid_options = gb.build()
    return grid_options
