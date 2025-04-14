import os
import logging
import io
import time
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm

from python.src.downloader.downloader import Downloader
from python.src.converter.archive_extractor import ExtractorFactory

PROCESSED_ZIP = "PROCESSED_ZIP"
ORIGINAL_TAR = "ORIGINAL_TAR"

MAX_DOWNLOAD_WORKERS = 5
DEFAULT_CHUNK_SIZE = 8192  # 8KB chunks

# This file is depricated, to download in bulk from archive please see the following
# website: https://blog.archive.org/2012/04/26/downloading-in-bulk-using-wget/

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


class BatchArchiveDownloader(Downloader):

    def __init__(self, config, download_type="PROCESSED_ZIP", extract_archives=True, trash_archives=True):
        self.input_list = config.get("input_list")
        self.save_folder = config.get("output_path")
        self.download_type = download_type
        self.extract_archives = extract_archives  # Flag to control extraction
        self.trash_archives = trash_archives      # Flag to control trashing archives after extraction
        self.progress_tracker = DownloadProgressTracker()

    def download_and_process_url(self, identifier):
        try:
            with requests.Session() as session:
                identifier = str.strip(identifier)

                # Get Archive identifier
                filename = self.create_filename(identifier, self.download_type)
                download_url = self.create_url(filename, identifier)
                save_path = os.path.join(self.save_folder, filename)

                if not os.path.exists(save_path):
                    # First, make a HEAD request to get the file size
                    head_response = session.head(download_url)
                    
                    # Binary Download
                    download_response = session.get(download_url, stream=True)

                    if download_response.status_code == 404:
                        filename = self.create_filename(identifier, PROCESSED_ZIP)
                        download_url = self.create_url(
                            filename,
                            identifier)
                        download_response = session.get(download_url, stream=True)
                        
                    # Get content length for progress bar or fallback to estimate
                    total_size = int(download_response.headers.get('content-length', 0))
                    
                    # Create progress bar
                    progress = self.progress_tracker.start_download(identifier, total_size)
                    
                    # Write the content to the file with progress updates
                    with open(save_path, 'wb') as fd:
                        for chunk in download_response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                            if chunk:  # Filter out keep-alive chunks
                                fd.write(chunk)
                                progress.update(len(chunk))
                    
                    self.progress_tracker.finish_download(identifier)
                    
                    # Show extraction message
                    if self.extract_archives:
                        print(f"Extracting {filename}...")
                
                # Extract archive if requested
                if self.extract_archives:
                    self.extract_archive(save_path, identifier)

        except Exception as e:
            logging.error(f"Error in download_and_process_url: {e}")
            # Make sure to finish the progress bar in case of error
            self.progress_tracker.finish_download(identifier)

    def extract_archive(self, archive_path, identifier):
        """
        Extract the downloaded archive if it's a supported format
        
        Args:
            archive_path (str): Path to the archive file
            identifier (str): Archive identifier for creating extraction folder
        """
        if not os.path.exists(archive_path):
            logging.warning(f"Archive file not found: {archive_path}")
            return
            
        # Create a subfolder for extraction using the identifier
        extract_dir = os.path.join(self.save_folder, identifier)
        
        # Create an extraction progress bar if the file is large enough
        file_size = os.path.getsize(archive_path)
        if file_size > 10 * 1024 * 1024:  # Only show for files > 10MB
            extract_progress = tqdm(
                total=100, 
                desc=f"Extracting {os.path.basename(archive_path)}", 
                leave=True
            )
            
            # Start a thread to update the progress bar during extraction
            stop_thread = threading.Event()
            
            def update_extract_progress():
                while not stop_thread.is_set():
                    if os.path.exists(extract_dir):
                        # Approximate progress by checking number of files
                        file_count = sum(len(files) for _, _, files in os.walk(extract_dir))
                        # Update progress (max 99 to leave final update for completion)
                        extract_progress.n = min(99, file_count)
                        extract_progress.refresh()
                    time.sleep(0.5)
            
            # Start progress update thread
            progress_thread = threading.Thread(target=update_extract_progress)
            progress_thread.daemon = True
            progress_thread.start()
        else:
            extract_progress = None
            stop_thread = None
            progress_thread = None
        
        try:
            # Get appropriate extractor for the file type
            extractor = ExtractorFactory.get_extractor(archive_path)
            if extractor:
                logging.info(f"Extracting {archive_path} to {extract_dir}")
                
                # Extract and optionally move to trash
                extractor.extract(
                    archive_path=archive_path, 
                    output_dir=extract_dir,
                    move_to_trash=self.trash_archives
                )
                
                if self.trash_archives:
                    logging.info(f"Archive file moved to trash after extraction: {archive_path}")
            else:
                logging.warning(f"No suitable extractor found for {archive_path}")
                
            # Complete the progress bar if it exists
            if extract_progress:
                extract_progress.n = 100
                extract_progress.refresh()
                extract_progress.close()
        finally:
            # Stop the progress update thread if it exists
            if stop_thread:
                stop_thread.set()
                if progress_thread:
                    progress_thread.join(timeout=1.0)

    def create_url(self, filename, identifier):
        download_url = f"https://archive.org/download/{identifier}/{filename}"
        return download_url

    def create_filename(self, identifier, download_type):
        if download_type == PROCESSED_ZIP:
            return f"{identifier}_jp2.zip"
        elif download_type == ORIGINAL_TAR:
            return f"{identifier}_orig_jp2.tar"
        else:
            raise NotImplemented()

    # Batch Downloader
    def download(self):
        # Create the save folder if it doesn't exist
        os.makedirs(self.save_folder, exist_ok=True)
        
        # Open the text file containing the image paths
        with open(self.input_list, 'r') as f:
            identifiers = list(tqdm(f, desc="Fetching URLs"))
            
            print(f"Downloading {len(identifiers)} book archives...")

            with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
                # Process each identifier with progress tracking
                list(tqdm(
                    executor.map(
                        self.download_and_process_url,
                        identifiers),
                    desc="Processing Books",
                    total=len(identifiers),
                    unit="book",
                    position=0,  # Main progress bar at the top
                    leave=True
                ))
            
            print(f"Downloaded and processed {len(identifiers)} book archives.")
