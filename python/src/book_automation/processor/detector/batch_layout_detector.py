from pathlib import Path
from typing import Dict, List
from PIL import Image

from book_automation.processor.detector.layout_detector import LayoutDetector
from book_automation.records.layout_elements import LayoutElement


class BatchLayoutDetector:
    """
    Runs layout detection on every image in a directory, using a pluggable LayoutDetector.
    """

    def __init__(self, input_dir: Path, detector: LayoutDetector):
        self.input_dir = input_dir
        self.detector = detector

    def detect(self) -> Dict[Path, List[LayoutElement]]:
        """
        Returns a dict mapping each image path to its list of detected LayoutElements.
        Only standard raster images are processed.
        """
        results: Dict[Path, List[LayoutElement]] = {}
        valid_suffixes = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}

        for img_path in sorted(self.input_dir.iterdir()):
            if not img_path.is_file() or img_path.suffix.lower() not in valid_suffixes:
                continue

            # 1) Load and normalize image
            with Image.open(img_path) as pil_img:
                img = pil_img.convert("RGB")

            # 2) Detect layout blocks
            blocks = self.detector.detect(img)

            # 3) Store results
            results[img_path] = blocks


        return results
