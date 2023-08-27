import os

import requests
from tqdm import tqdm

from python.src.downloader.downloader import Downloader
from python.src.generator.url_generator import UrlGenerator


def create_image_name(i):
    return f"image_{str.zfill(str(i), 4)}.png"


class NumberedUrlBookDownloader(Downloader):

    def __init__(self,
                 url_generator: UrlGenerator,
                 num_pages: int = None,
                 output_path: str = None):
        self.url_generator = url_generator
        self.output_path = output_path
        self.num_pages = num_pages

    def download_images(self):
        for i in tqdm(range(1, self.num_pages)):
            url = self.url_generator.generate_url(i)
            self.download_and_save(i, url)

    def download_and_save(self, i, url):
        response = requests.get(url)
        if response.status_code == 200:
            file_path = os.path.join(self.output_path, create_image_name(i))
            with open(file_path, 'wb') as image_file:
                image_file.write(response.content)
            print(f"Downloaded {self.output_path}")
        else:
            print(f"Failed to download image from {url}")
