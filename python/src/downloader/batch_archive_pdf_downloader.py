import os
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm

from python.src.downloader.downloader import Downloader

PROCESSED_ZIP = "PROCESSED_ZIP"
ORIGINAL_TAR = "ORIGINAL_TAR"

MAX_DOWNLOAD_WORKERS = 5

# This file is depricated, to download in bulk from archive please see the following
# website: https://blog.archive.org/2012/04/26/downloading-in-bulk-using-wget/

class BatchArchiveDownloader(Downloader):

    def __init__(self, config, download_type="PROCESSED_ZIP"):
        self.input_list = config.get("input_list")
        self.save_folder = config.get("output_path")
        self.download_type = download_type

    def download_and_process_url(self, identifier):
        try:
            with requests.Session() as session:
                identifier = str.strip(identifier)

                # Get Archive identifier
                filename = self.create_filename(identifier, self.download_type)
                download_url = self.create_url(filename, identifier)
                save_path = os.path.join(self.save_folder, filename)

                if not os.path.exists(save_path):

                    # Binary Download
                    response = session.get(download_url)

                    if response.status_code == 404:
                        filename = self.create_filename(identifier, PROCESSED_ZIP)
                        download_url = self.create_url(
                            filename,
                            identifier)
                        response = session.get(download_url)

                    # Write the content to the file
                    with open(save_path, 'wb') as fd:
                        for chunk in response.iter_content(chunk_size=8192):
                            fd.write(chunk)

        except Exception as e:
            print(f"Error in download_and_process_url: {e}")

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
        # Open the text file containing the image paths
        with open(self.input_list, 'r') as f:
            identifiers = list(tqdm(f, desc="Fetching URLs"))

            with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
                tqdm(
                    executor.map(
                        self.download_and_process_url,
                        identifiers),
                    desc="Downloading and Processing",
                    total=len(identifiers))
