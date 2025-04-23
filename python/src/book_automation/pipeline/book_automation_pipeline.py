import os
import time
from pathlib import Path
from typing import Dict

from batch_image_processor.processors.image.deskew import Deskew
from batch_image_processor.processors.image.page_cropper import PageCropper
from batch_image_processor.processors.single_page_processor import SinglePageProcessor

from book_automation.externals.gpt_vision_client import GPTVisionClient
from book_automation.pipeline.threaded_book_runner import ThreadedBookRunner
from book_automation.processor.converter.pil_image_converter import PilImageConverter
from book_automation.processor.detector.LayoutParserDetector import LayoutParserDetector
from book_automation.processor.detector.batch_layout_detector import BatchLayoutDetector
from book_automation.processor.detector.document_ai_layout_detector import DocumentAILayoutDetector
from book_automation.records.page_type import PageType
from book_automation.scantailor.scantailor_service import ScanTailorService
from book_automation.sorter.classifier.gpt_vision_page_type_classifier import \
    GPTVisionPageTypeClassifier
from book_automation.sorter.image_sorter import ImageSorter
from book_automation.util.zip_util import ZipUtil
from python.src.book_automation.downloader.archive_downloader import ArchiveDownloader


class BookAutomationPipeline:

    def __init__(self, config: Dict):
        self.book_id = config['book_id']
        self.book_title = config['book_title']
        self.book_projects_path = config['book_projects_path']

    def run(self):
        book_dir = os.path.join(self.book_projects_path, self.book_title)
        #
        # zip_path = ArchiveDownloader(self.book_projects_path, self.book_id).download()
        #
        # book_dir = ZipUtil.extract_zip(zip_path, book_dir)
        # os.remove(zip_path)
        #
        # time.sleep(10)

        image_path = os.path.join(book_dir, self.book_id + "_jp2")
        png_path = os.path.join(book_dir, "out")
        tailored_path = os.path.join(book_dir, "tailored")
        deskewed_path = os.path.join(book_dir, "deskewed")
        sorted_path = os.path.join(book_dir, "sorted")
        content_path = os.path.join(sorted_path, PageType.CONTENT_PAGE.value)
        content_upscaled_path = os.path.join(sorted_path, PageType.CONTENT_PAGE.value + "_upscaled")

        ThreadedBookRunner(
            processor=PilImageConverter(),
            input_dir=image_path,
            output_dir=png_path,
            file_pattern="*.jp2").run()
        #
        # ScanTailorService(dpi=300).process_images(png_path, tailored_path)
        #
        # SinglePageProcessor(
        #     input_dir=png_path,
        #     output_dir=deskewed_path,
        #     processors=[
        #         PageCropper(),
        #         Deskew()
        #     ]
        # ).batch_process()
        #
        # ImageSorter(
        #     input_dir=Path(deskewed_path),
        #     output_dir=Path(sorted_path),
        #     classifier=GPTVisionPageTypeClassifier(
        #         types=[PageType.BLANK_PAGE, PageType.CONTENT_PAGE],
        #         vision_client=GPTVisionClient()
        #     )
        # ).sort()

        CloudProcessorRunner(
            input_dir=Path(content_path),
            output_dir=Path(content_upscaled_path),
        )





if __name__ == "__main__":
    config_path = "/Users/iankonradjohnson/base/abacus/BookDownloader/config/automation/pipeline.yml"

    config = None
    with open(config_path, 'r') as file:
        import yaml

        config = yaml.safe_load(file)

    BookAutomationPipeline(config).run()
