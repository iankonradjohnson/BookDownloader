import os
from concurrent.futures import ThreadPoolExecutor

import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

from typing import List

from tqdm import tqdm

from python.src.util.file_utility import FileUtility


class BatchDownloader:

    def __init__(self, output_dir):
        self.output_dir = output_dir

    def batch_download(self, urls: List[str]):

        with ThreadPoolExecutor() as executor:
            list(
                tqdm(
                    executor.map(self.download_image, urls, range(len(urls))),
                    total=len(urls),
                )
            )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def download_image(self, url: str, i: int):
        try:
            response = requests.get(url)
            response.raise_for_status()
            path = os.path.join(self.output_dir, FileUtility.create_image_name(i))
            with open(path, 'wb') as f:
                f.write(response.content)
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")