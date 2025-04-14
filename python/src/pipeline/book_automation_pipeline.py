import os
from typing import Dict

from python.src.factory.image_downloader_factory import ImageDownloaderFactory
from python.src.investigator.book_investigator import BookInvestigator
from python.src.records.book_data import BookData
from python.src.util.zip_util import ZipUtil




class BookAutomationPipeline:

    def __init__(self, config: Dict):
        self.book_downloader = ArchiveDownloader(config[])
        self.book_investigator = BookInvestigator()

        self.book_id = config['book_id']
        self.book_projects_path = config['book_projects_path']

    def run(self):
        self.book_downloader.download()

        book_data: BookData = self.book_investigator.investigate(self.book_id)
        book_dir = ZipUtil.extract_and_rename(self.book_projects_path, book_data.title)





if __name__ == "__main__":
    config_path = "/Users/iankonradjohnson/base/abacus/BookDownloader/config/automation/pipeline.yml"

    config = None
    with open(config_path, 'r') as file:
        import yaml
        config = yaml.safe_load(file)

    BookAutomationPipeline(config).run()
