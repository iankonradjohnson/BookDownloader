import os

import requests
from tqdm import tqdm

from python.src.book_automation.downloader.downloader import Downloader
from python.src.book_automation.generator.url_generator import UrlGenerator
from python.src.book_automation.util.file_utility import FileUtility


class NumberedUrlBookDownloader(Downloader):

    def __init__(self,
                 url_generator: UrlGenerator, config):
        self.url_generator = url_generator
        self.output_path = config['output_path']
        self.num_pages = config['num_pages']
        self.offset = config['offset']

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

    def download(self):
        for i in tqdm(range(self.offset, self.num_pages)):
            url = self.url_generator.generate_url(i)
            self.download_and_save(i, url)

    def download_and_save(self, i, url):
        completed = False
        while not completed:
            try:
                response = requests.get(url)
            except Exception as e:
                print(e)
                continue

            if response.status_code == 200:
                file_path = os.path.join(self.output_path, FileUtility.create_image_name(i))
                with open(file_path, 'wb') as image_file:
                    image_file.write(response.content)
                print(f"Downloaded {self.output_path}")
            else:
                print(f"Response was not successful for {url}, skipping.")
            completed = True
