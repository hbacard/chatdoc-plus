"""Abstract class for a streamlit page. A page is a container of st_sections and other elements,
and its instances are launched by the app.py module in the root of the library.
"""
from abc import ABC, abstractmethod


class AbcPage(ABC):
    """An abstract class for rendering a streamlit page"""

    @abstractmethod
    def display(self):
        """Renders a streamlit page"""
