from abc import ABC, abstractmethod
from pathlib import Path

from book_automation.processor.directory.image_directory_processor import ImageDirectoryProcessor


class CloudBatchRunner(ABC):
    def __init__(self, input_dir: Path, output_dir: Path, image_directory_processor: ImageDirectoryProcessor):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.processor = image_directory_processor

    @abstractmethod
    def run(self):
        pass