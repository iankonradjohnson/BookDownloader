from dataclasses import dataclass
from typing import Tuple


@dataclass
class LayoutElement:
    """
    A single detected region on the page.
    - type: semantic role (e.g. "TITLE", "SECTION_HEADING", "PARAGRAPH", "FOOTNOTE", "FIGURE")
    - bbox: (x_min, y_min, x_max, y_max) in pixel coordinates
    - confidence: float [0–1]
    """
    type: str
    bbox: Tuple[int, int, int, int]
    confidence: float