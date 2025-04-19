from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

from PIL import Image
from tqdm import tqdm

from book_automation.sorter.classifier.page_type_classifier import PageTypeClassifier


class ImageSorter:
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        classifier: PageTypeClassifier,
        max_workers: int = None
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.classifier = classifier
        self.max_workers = max_workers

        # Ensure output subdirectories exist for each page type
        for pt in classifier.types:
            (self.output_dir / pt.value).mkdir(parents=True, exist_ok=True)

    def _process_image(self, img_path: Path) -> None:
        try:
            with Image.open(img_path) as img:
                page_type = self.classifier.classify(img)

            dest_dir = self.output_dir / page_type.value
            img_path.rename(dest_dir / img_path.name)
        except Exception as e:
            # Consider logging instead of printing in production
            print(f"Error processing {img_path.name}: {e}")

    def sort(self) -> None:
        image_paths: List[Path] = [p for p in self.input_dir.iterdir() if p.is_file()]
        total = len(image_paths)

        # Use ThreadPoolExecutor for I/O-bound tasks
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # executor.map returns an iterator; wrap with tqdm for progress
            for _ in tqdm(executor.map(self._process_image, image_paths), total=total, desc="Sorting images"):
                pass
