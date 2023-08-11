from image_downloader import ImageDownloader


class RaraDownloader(ImageDownloader):
    def __init__(self, config):
        super().__init__(config.get("num_pages"), config.get("output_path"))
        self.start_id = config.get("start_id")

    def generate_url(self, page_num):
        return f"https://www.e-rara.ch/zut/download/webcache/0/{self.start_id + page_num}"
