import logging
import os
import string
import threading

import requests
from tqdm import tqdm

from python.src.downloader.batch_archive_pdf_downloader import PROCESSED_ZIP, ORIGINAL_TAR, \
    DEFAULT_CHUNK_SIZE
from python.src.downloader.downloader import Downloader


class ArchiveDownloader(Downloader):
    def __init__(self, save_folder, book_id, download_type="PROCESSED_ZIP"):
        self.save_folder = save_folder
        self.book_id = book_id
        self.download_type = download_type
        self.progress_tracker = None

    def download(self) -> str:
        self.progress_tracker = DownloadProgressTracker()
        try:
            with requests.Session() as session:
                identifier = str.strip(self.book_id)
                filename = self.create_filename(identifier, self.download_type)
                download_url = self.create_url(filename, identifier)
                save_path = os.path.join(self.save_folder, filename)

                if not os.path.exists(save_path):
                    download_response = session.get(download_url, stream=True)

                    if download_response.status_code == 404:
                        filename = self.create_filename(identifier, PROCESSED_ZIP)
                        download_url = self.create_url(filename, identifier)
                        download_response = session.get(download_url, stream=True)

                    total_size = int(download_response.headers.get('content-length', 0))

                    progress = None
                    if self.progress_tracker:
                        progress = self.progress_tracker.start_download(identifier, total_size)

                    with open(save_path, 'wb') as fd:
                        for chunk in download_response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                            if chunk:
                                fd.write(chunk)
                                if progress:
                                    progress.update(len(chunk))

                    if self.progress_tracker:
                        self.progress_tracker.finish_download(identifier)

                return save_path

        except Exception as e:
            logging.error(f"Error downloading archive: {e}")
            if self.progress_tracker:
                self.progress_tracker.finish_download(identifier)
            return None

    def create_url(self, filename, identifier):
        return f"https://archive.org/download/{identifier}/{filename}"

    def create_filename(self, identifier, download_type):
        if download_type == PROCESSED_ZIP:
            return f"{identifier}_jp2.zip"
        elif download_type == ORIGINAL_TAR:
            return f"{identifier}_orig_jp2.tar"
        else:
            raise NotImplemented()


class DownloadProgressTracker:
    """
    Helper class to track download progress across multiple threads
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.active_downloads = {}

    def start_download(self, identifier, total_size):
        """Register a new download and return the progress bar"""
        with self.lock:
            progress_bar = tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=f"Downloading {identifier}",
                leave=True
            )
            self.active_downloads[identifier] = progress_bar
            return progress_bar

    def update_progress(self, identifier, chunk_size):
        """Update the progress for a specific download"""
        with self.lock:
            if identifier in self.active_downloads:
                self.active_downloads[identifier].update(chunk_size)

    def finish_download(self, identifier):
        """Mark a download as complete and close its progress bar"""
        with self.lock:
            if identifier in self.active_downloads:
                self.active_downloads[identifier].close()
                del self.active_downloads[identifier]