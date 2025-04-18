from pathlib import Path
from typing import List

from PIL import Image

from book_automation.records.page_type import PageType
from book_automation.sorter.classifier.page_type_classifier import PageTypeClassifier


class ImageSorter:
    """
    Sorts images from an input directory into subdirectories under the output directory
    based on the classification provided by a PageTypeClassifier.
    """
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        classifier: PageTypeClassifier
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.classifier = classifier

        # Ensure output subdirectories exist for each page type
        for pt in classifier.types:
            (self.output_dir / pt.value).mkdir(parents=True, exist_ok=True)

    def sort(self) -> None:
        """
        Processes all files in the input directory, classifies each image,
        and moves it into the corresponding subdirectory in the output directory.
        """
        for img_path in self.input_dir.iterdir():
            if not img_path.is_file():
                continue
            try:
                with Image.open(img_path) as img:
                    page_type = self.classifier.classify(img)

                dest_dir = self.output_dir / page_type.value
                # Move the file into its classified directory
                img_path.rename(dest_dir / img_path.name)

            except Exception as e:
                print(f"Error processing {img_path.name}: {e}")