import os
from abc import abstractmethod

import requests
from tqdm import tqdm

class ImageDownloader:

    def __init__(self, num_pages=None, output_path=None):
        self.output_path = output_path
        self.num_pages = num_pages

    def download_images(self):
        for i in tqdm(range(1, self.num_pages)):
            url = self.generate_url(i)
            response = requests.get(url)
            if response.status_code == 200:
                file_path = os.path.join(self.output_path, self.create_image_name(i))
                with open(file_path, 'wb') as image_file:
                    image_file.write(response.content)
                print(f"Downloaded {self.output_path}")
            else:
                print(f"Failed to download image from {url}")

    def create_image_name(self, i):
        return f"image_{str.zfill(str(i), 4)}.png"

    @abstractmethod
    def generate_url(self, page_num):
        pass









