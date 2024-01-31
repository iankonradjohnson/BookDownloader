import requests

from python.src.downloader.batch_downloader import BatchDownloader
from python.src.downloader.downloader import Downloader
from python.src.generator.rara_url_generator import RaraUrlGenerator


class RaraManifestBookDownloader(Downloader):

    def __init__(self, manifest_url, output_dir, structure_id):
        self.manifest_url = manifest_url
        self.structure_id = structure_id
        self.batch_downloader = BatchDownloader(output_dir)

    def download(self):
        manifest_json = requests.get(self.manifest_url).json()
        structures = manifest_json['structures']
        urls = [structure['canvases'] for structure in structures if structure['@id'] == self.structure_id][0]
        ids = [url.split('/')[-1] for url in urls]

        image_urls = [RaraUrlGenerator.generate_url_from_id(image_id) for image_id in ids]

        self.batch_downloader.batch_download(image_urls)

