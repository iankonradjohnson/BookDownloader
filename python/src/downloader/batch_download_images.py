import os
import sys
import requests
from tqdm import tqdm

from os import path as osp

from python.src.downloader.downloader import Downloader


class BatchImageDownloader(Downloader):
    def __init__(self, input_list=None, output_dir=None):
        self.input_list = input_list
        self.output_dir = output_dir

    def download(self):

        if not osp.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f'mkdir {self.output_dir} ...')
        else:
            print(f'Folder {self.output_dir} already exists. Exit.')
            sys.exit(1)

        with open(self.input_list, 'r') as f:
            for line in tqdm(f):
                line = line.strip()
                save_path = os.path.join(self.output_dir, line.split('/')[-2])
                r = requests.get(line)
                with open(save_path + ".png", 'wb') as f:
                    f.write(r.content)
