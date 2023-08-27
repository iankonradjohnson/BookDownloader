from python.src.generator.url_generator import UrlGenerator


class RaraUrlGenerator(UrlGenerator):
    def __init__(self, config):
        self.start_id = config.get("start_id")

    def generate_url(self, page_num):
        return f"https://www.e-rara.ch/zut/download/webcache/0/{self.start_id + page_num}"
