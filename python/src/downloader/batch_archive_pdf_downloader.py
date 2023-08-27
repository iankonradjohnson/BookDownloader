import os
import shutil
import zipfile
from io import BytesIO
import requests
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from python.src.downloader.downloader import Downloader

MAX_DOWNLOAD_WORKERS = 10


class BatchArchivePdfDownloader(Downloader):

    def __init__(self, config):
        self.input_list = config.get("input_list")
        self.save_folder = config.get("output_path")

    def process_file(self, file_name, extracted_folder):
        try:
            if file_name.endswith(".jp2"):
                file_path = os.path.join(extracted_folder, file_name)
                with Image.open(file_path) as image:
                    png_file_name = os.path.splitext(file_name)[0] + ".png"
                    png_path = os.path.join(self.save_folder, png_file_name)
                    image.save(png_path, format="PNG")
                os.remove(file_path)  # remove the original .jp2 file after conversion
        except Exception as e:
            print(f"Error at page level on {file_name}: {e}")

    def download_and_process_url(self, url):
        try:
            with requests.Session() as session:
                # Extract the book identifier from the URL
                identifier = url.split("/")[-5]
                download_url = f"https://archive.org/download/{identifier}/{identifier}_jp2.zip"

                # Download the zip file and extract the JP2 images
                response = session.get(download_url)
                zip_file = BytesIO(response.content)
                extracted_folder = os.path.join(self.save_folder, identifier + "_jp2")

                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(self.save_folder)

                files_in_folder = os.listdir(extracted_folder)
                if not files_in_folder:  # check if the folder is empty
                    print(f"No files found in {extracted_folder}")
                    return

                # Parallelize the processing part for each downloaded content
                with ThreadPoolExecutor() as executor:
                    list(tqdm(executor.map(self.process_file, files_in_folder,
                                           [extracted_folder] * len(files_in_folder)),
                              desc="Converting Images"))

                # You can remove this line if you want to keep the extracted folder intact
                # shutil.rmtree(extracted_folder)

        except Exception as e:
            print(f"Error in download_and_process_url: {e}")

    def download(self):
        # Open the text file containing the image paths
        with open(self.input_list, 'r') as f:
            urls = list(tqdm(f, desc="Fetching URLs"))

            with ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(self.download_and_process_url, urls), desc="Downloading and Processing",
                          total=len(urls)))
