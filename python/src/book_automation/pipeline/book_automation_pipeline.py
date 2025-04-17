import os
from typing import Dict

# Import directly from the BatchImageProcessor project path
from batch_image_processor_project.python.src.processors.batch.batch_processor import BatchProcessor

from python.src.book_automation.downloader.archive_downloader import ArchiveDownloader
from python.src.book_automation.investigator.book_investigator import BookInvestigator
from python.src.book_automation.records.book_data import BookData


class BookAutomationPipeline:

    def __init__(self, config: Dict):
        self.book_id = config['book_id']
        self.book_projects_path = config['book_projects_path']

        self.book_investigator = BookInvestigator(self.book_id)
        self.downloader = ArchiveDownloader(self.book_projects_path, self.book_id)

    def run(self):
        book_data: BookData = self.book_investigator.investigate()
        book_dir = os.path.join(self.book_projects_path, book_data.title)
        #
        # zip_path = self.downloader.download()
        #
        # book_dir = ZipUtil.extract_zip(zip_path, book_dir)
        # os.remove(zip_path)

        # image_path = os.path.join(book_dir, self.book_id + "_jp2")
        png_path = os.path.join(book_dir, "out")
        #
        # ThreadedBookRunner(
        #     processor=PilImageConverter(),
        #     input_dir=image_path,
        #     output_dir=png_path,
        #     file_pattern="*.jp2").run()

        tailored_path = os.path.join(book_dir, "tailored")

        # ScanTailorService().process_images(png_path, tailored_path)

        processors = []
        batch_processor = BatchProcessor(
            input_dir=tailored_path,
            output_dir=os.path.join(book_dir, "processed"),
            processors=processors
        )


if __name__ == "__main__":
    config_path = "/config/automation/pipeline.yml"

    config = None
    with open(config_path, 'r') as file:
        import yaml

        config = yaml.safe_load(file)

    BookAutomationPipeline(config).run()
