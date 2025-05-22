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
from book_automation.pipeline.threaded_book_runner import ThreadedBookRunner
from book_automation.processor.converter.pil_image_converter import PilImageConverter
from book_automation.processor.csv_generator.image_folder_csv_creator import ImageFolderCsvCreator
from book_automation.util.zip_util import ZipUtil

# Load environment variables
load_dotenv()


class BookAutomationPipelineSimple:
    """
    A simplified version of the BookAutomationPipeline that skips the image sorting and RunPod steps.
    This pipeline contains the following steps:
    1. Download the book archive
    2. Extract the archive
    3. Convert JP2 images to PNG
    4. Deskew and crop the images
    5. Apply threshold and border processing directly on the deskewed images
    6. Generate CSV file for the processed images
    """

    def __init__(self, config: Dict):
        self.book_id = config['book_id']
        self.book_title = config['book_title']
        self.book_projects_path = config['book_projects_path']

    def run(self):
        book_dir = os.path.join(self.book_projects_path, self.book_title)
        zip_filename = f"{self.book_id}_jp2.zip"
        zip_path = os.path.join(self.book_projects_path, zip_filename)
        
        # Step 1: Download the book archive (if needed)
        if not os.path.exists(zip_path) and not os.path.exists(book_dir):
            zip_path = ArchiveDownloader(self.book_projects_path, self.book_id).download()
        else:
            print(f"Zip file {zip_path} already exists. Skipping download.")
            
        # Step 2: Extract the archive (if needed)
        if not os.path.exists(book_dir):
            print("Extracting zip...")
            book_dir = ZipUtil.extract_zip(zip_path, book_dir)
            os.remove(zip_path)
            time.sleep(10)
        else:
            print(f"Book directory {book_dir} already exists. Skipping extraction.")

        # Define paths for each processing step
        image_path = os.path.join(book_dir, self.book_id + "_jp2")
        png_path = os.path.join(book_dir, "out")
        deskewed_path = os.path.join(book_dir, "deskewed")
        processed_path = os.path.join(book_dir, "processed")
        csv_path = os.path.join(processed_path, "out.csv")

        # Step 3: Convert JP2 images to PNG (if needed)
        if not os.path.exists(png_path):
            print("Converting JP2 images to PNG...")
            ThreadedBookRunner(
                processor=PilImageConverter(),
                input_dir=image_path,
                output_dir=png_path,
                file_pattern="*.jp2").run()

        # Step 4: Deskew and crop the images (if needed)
        if not os.path.exists(deskewed_path):
            print("Deskewing and cropping images...")
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

        # Step 5: Apply threshold and border processing directly on the deskewed images (if needed)
        # Skip image sorting and RunPod upscaling
        if not os.path.exists(processed_path):
            print("Applying threshold and border processing...")
            BatchProcessor(
                input_dir=deskewed_path,
                output_dir=processed_path,
                processors=[
                    ThresholdProcessor(threshold_value=190),
                    ImageModeConverter(mode="1"),
                    # BorderProcessor(top=350, bottom=400, left=300, right=450)
                ],
                pipeline_class=ImagePipeline,
                parallel=True
            ).batch_process()

        # Step 6: Generate CSV file for the processed images (if needed)
        if not os.path.exists(csv_path):
            print("Generating CSV file...")
            ImageFolderCsvCreator(
                img_dir=Path(processed_path),
                csv_path=Path(csv_path)
            ).create()
            
        print(f"Processing complete. Final images and CSV available at: {processed_path}")


if __name__ == "__main__":
    config_path = "/Users/iankonradjohnson/base/abacus/BookDownloader/config/automation/pipeline.yml"

    config = None
    with open(config_path, 'r') as file:
        import yaml
        config = yaml.safe_load(file)

    # Remove RunPod pod ID if it's in the config since we don't need it
    if 'runpod_pod_id' in config:
        del config['runpod_pod_id']

    BookAutomationPipelineSimple(config).run()