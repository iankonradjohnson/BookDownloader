from abc import ABC
from enum import Enum
from typing import Protocol, Generic, TypeVar, List

from PIL import Image

from book_automation.externals.gpt_vision_client import GPTVisionClient
from book_automation.records.page_type import PageType
from book_automation.sorter.classifier.page_type_classifier import PageTypeClassifier


class GPTVisionPageTypeClassifier(PageTypeClassifier):

    def __init__(self, types: List[PageType], vision_client: GPTVisionClient):
        super().__init__(types)
        self.prompt = self._create_prompt()
        self.vision_client = vision_client

    def _create_prompt(self) -> str:
        types_str = '\n'.join([item.value for item in self.types])

        return f"""
        Classify this image according to the following types: 
        
        {types_str}
        
        Just output the type, thats it.
        
        """

    def classify(self, image: Image.Image) -> PageType:
        return PageType(self.vision_client.invoke(image, self.prompt))
