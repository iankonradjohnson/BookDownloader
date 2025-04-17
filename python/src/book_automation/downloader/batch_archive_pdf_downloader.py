import os
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

from python.src.book_automation.downloader.downloader import Downloader

PROCESSED_ZIP = "PROCESSED_ZIP"
ORIGINAL_TAR = "ORIGINAL_TAR"

MAX_DOWNLOAD_WORKERS = 5
DEFAULT_CHUNK_SIZE = 8192  # 8KB chunks

# This file is depricated, to download in bulk from archive please see the following
# website: https://blog.archive.org/2012/04/26/downloading-in-bulk-using-wget/

class BatchArchiveDownloader(Downloader):
    def __init__(self, config, download_type="PROCESSED_ZIP", extract_archives=True, trash_archives=True):
        self.input_list = config.get("input_list")
        self.save_folder = config.get("output_path")
        self.download_type = download_type
        self.extract_archives = extract_archives
        self.trash_archives = trash_archives
        self.progress_tracker = DownloadProgressTracker()
        self.archive_downloader = ArchiveDownloader(
            self.save_folder, 
            self.download_type,
            self.extract_archives,
            self.trash_archives
        )

    def download_and_process_url(self, identifier):
        return self.archive_downloader.download(identifier, self.progress_tracker)

    def download(self):
        os.makedirs(self.save_folder, exist_ok=True)
        
        with open(self.input_list, 'r') as f:
            identifiers = list(tqdm(f, desc="Fetching URLs"))
            
            print(f"Downloading {len(identifiers)} book archives...")

            with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
                list(tqdm(
                    executor.map(
                        self.download_and_process_url,
                        identifiers),
                    desc="Processing Books",
                    total=len(identifiers),
                    unit="book",
                    position=0,
                    leave=True
                ))
            
            print(f"Downloaded and processed {len(identifiers)} book archives.")
