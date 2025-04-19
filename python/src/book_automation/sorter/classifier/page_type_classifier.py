from abc import ABC
from enum import Enum
from typing import Protocol, Generic, TypeVar, List

from PIL import Image

from book_automation.records.page_type import PageType


class PageTypeClassifier(ABC):

    def __init__(self, types: List[PageType]):
        self.types = types

    def classify(self, image: Image.Image) -> PageType:
        pass