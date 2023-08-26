import os
import shutil
import zipfile
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm

from downloader.downloader import Downloader


class BatchArchivePdfDownloader(Downloader):

    def __init__(self, config):
        self.input_list = config.get("input_list")
        self.save_folder = config.get("output_path")

    def download(self):
        # Open the text file containing the image paths
        with open(self.input_list, 'r') as f:
            # Loop through each line in the file
            for url in tqdm(f):
                try:
                    # Extract the book identifier from the URL
                    identifier = url.split("/")[-5]
                    # Construct the download URL for the PDF file
                    url = f"https://archive.org/download/{identifier}/{identifier}_jp2.zip"
                    # Download the zip file and extract the JP2 images
                    response = requests.get(url)
                    zip_file = BytesIO(response.content)
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall()

                    folder_name = os.path.splitext(os.path.basename(url))[0]
                    extracted_folder = os.path.join(os.getcwd(), folder_name)

                    for file_name in tqdm(os.listdir(extracted_folder)):
                        try:
                            if file_name.endswith(".jp2"):
                                file_path = os.path.join(extracted_folder, file_name)
                                with Image.open(file_path) as image:
                                    png_file_name = os.path.splitext(file_name)[0] + ".png"
                                    png_path = os.path.join(self.save_folder, png_file_name)
                                    image.save(png_path, format="PNG")
                                    os.remove(file_path)
                        except Exception as e:
                            print(f"Error at page level on {file_name}: {e}")

                    shutil.rmtree(extracted_folder)
                except Exception as e:
                    print(f"Error at book level on {f}: {e}")
                    continue
