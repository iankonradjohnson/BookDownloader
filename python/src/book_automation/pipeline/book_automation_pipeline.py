import os
import time
from pathlib import Path
from typing import Dict

from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.image.border_processor import BorderProcessor
from batch_image_processor.processors.image.deskew import Deskew
from batch_image_processor.processors.image.image_mode_converter import ImageModeConverter
from batch_image_processor.processors.image.page_cropper import PageCropper
from batch_image_processor.processors.image.threshold_processor import ThresholdProcessor
from batch_image_processor.processors.pipeline import ImagePipeline
from dotenv import load_dotenv

from book_automation.downloader.archive_downloader import ArchiveDownloader
from book_automation.externals.gpt_vision_client import GPTVisionClient
from book_automation.scantailor.scantailor_service import ScanTailorService
from book_automation.sorter.classifier.gpt_vision_page_type_classifier import \
    GPTVisionPageTypeClassifier
from book_automation.sorter.image_sorter import ImageSorter
from book_automation.util.zip_util import ZipUtil

# Load environment variables
load_dotenv()

from book_automation.pipeline.threaded_book_runner import ThreadedBookRunner
from book_automation.processor.cloud.runpod.runpod_batch_runner import RunPodBatchRunner
from book_automation.processor.converter.pil_image_converter import PilImageConverter
from book_automation.processor.csv_generator.image_folder_csv_creator import ImageFolderCsvCreator
from book_automation.records.page_type import PageType


class BookAutomationPipeline:

    def __init__(self, config: Dict):
        self.book_id = config['book_id']
        self.book_title = config['book_title']
        self.book_projects_path = config['book_projects_path']
        self.runpod_pod_id = config['runpod_pod_id']

    def run(self):
        book_dir = os.path.join(self.book_projects_path, self.book_title)
        zip_filename = f"{self.book_id}_jp2.zip"
        zip_path = os.path.join(self.book_projects_path, zip_filename)
        
        if not os.path.exists(zip_path) and not os.path.exists(book_dir):
            zip_path = ArchiveDownloader(self.book_projects_path, self.book_id).download()
        else:
            print(f"Zip file {zip_path} already exists. Skipping download.")
            
        if not os.path.exists(book_dir):
            print("Extracting zip...")
            book_dir = ZipUtil.extract_zip(zip_path, book_dir)
            os.remove(zip_path)
            time.sleep(10)
        else:
            print(f"Book directory {book_dir} already exists. Skipping extraction.")

        image_path = os.path.join(book_dir, self.book_id + "_jp2")
        png_path = os.path.join(book_dir, "out")
        deskewed_path = os.path.join(book_dir, "deskewed")
        sorted_path = os.path.join(book_dir, "sorted")
        content_path = os.path.join(sorted_path, PageType.CONTENT_PAGE.value)
        content_upscaled_path = os.path.join(sorted_path, PageType.CONTENT_PAGE.value + "_upscaled")
        threshold_path = os.path.join(sorted_path, PageType.CONTENT_PAGE.value + "_upscaled_threshold")
        csv_path = os.path.join(threshold_path, "out.csv")

        if not os.path.exists(png_path):
            ThreadedBookRunner(
                processor=PilImageConverter(),
                input_dir=image_path,
                output_dir=png_path,
                file_pattern="*.jp2").run()

        if not os.path.exists(deskewed_path):
            BatchProcessor(
                input_dir=png_path,
                output_dir=deskewed_path,
                processors=[
                    # PageCropper(),
                    Deskew()
                ],
                pipeline_class=ImagePipeline,
                parallel=True
            ).batch_process()

        if not os.path.exists(sorted_path):
            ImageSorter(
                input_dir=Path(deskewed_path),
                output_dir=Path(sorted_path),
                classifier=GPTVisionPageTypeClassifier(
                    types=[PageType.BLANK_PAGE, PageType.CONTENT_PAGE],
                    vision_client=GPTVisionClient()
                )
            ).sort()

        if not os.path.exists(content_upscaled_path):
            RunPodBatchRunner(
                runpod_pod_id=self.runpod_pod_id,
                input_dir=Path(content_path),
                output_dir=Path(content_upscaled_path),
            ).run()

        if not os.path.exists(threshold_path):
            BatchProcessor(
                input_dir=content_upscaled_path,
                output_dir=threshold_path,
                processors=[
                    ThresholdProcessor(threshold_value=120),
                    ImageModeConverter(mode="1"),
                    BorderProcessor(top=20, bottom=20, left=20, right=20)
                ],
                pipeline_class=ImagePipeline,
                parallel=True
            ).batch_process()

        if not os.path.exists(csv_path):
            ImageFolderCsvCreator(
                img_dir=Path(threshold_path),
                csv_path=Path(csv_path)
            ).create()







if __name__ == "__main__":
    config_path = "/Users/iankonradjohnson/base/abacus/BookDownloader/config/automation/pipeline.yml"

    config = None
    with open(config_path, 'r') as file:
        import yaml

        config = yaml.safe_load(file)

    BookAutomationPipeline(config).run()
