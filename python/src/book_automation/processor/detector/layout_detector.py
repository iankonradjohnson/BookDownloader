from abc import ABC, abstractmethod
from typing import List

from PIL import Image

from book_automation.records.layout_elements import LayoutElement


class LayoutDetector(ABC):
    @abstractmethod
    def detect(self, image: Image.Image) -> List[LayoutElement]:
        """
        Given a PIL image, returns a list of LayoutElements.
        """
        ...
