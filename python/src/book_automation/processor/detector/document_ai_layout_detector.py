# book_automation/processor/detector/document_ai_layout_detector.py

from typing import List
from PIL import Image

from book_automation.processor.detector.layout_detector import LayoutDetector
from book_automation.externals.document_ai_client import DocumentAIClient
from book_automation.records.layout_elements import LayoutElement


class DocumentAILayoutDetector(LayoutDetector):
    def __init__(self):
        self.client = DocumentAIClient()

    def detect(self, image: Image.Image) -> List[LayoutElement]:
        document = self.client.process_image(image)
        elements: List[LayoutElement] = []

        for page in document.pages:
            for paragraph in page.paragraphs:
                layout = paragraph.layout
                xs = [v.x for v in layout.bounding_poly.vertices]
                ys = [v.y for v in layout.bounding_poly.vertices]
                bbox = (min(xs), min(ys), max(xs), max(ys))
                elements.append(
                    LayoutElement(
                        type="paragraph",
                        bbox=bbox,
                        confidence=layout.confidence
                    )
                )

        return elements
