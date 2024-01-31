from python.src.generator.url_generator import UrlGenerator

URL_FORMAT = "https://www.e-rara.ch/zut/download/webcache/0/{image_id}"

class RaraUrlGenerator(UrlGenerator):


    def __init__(self, config=None):
        self.start_id = config.get("start_id", "")

    def generate_url(self, page_num):
        return URL_FORMAT.format(image_id=self.start_id + page_num)

    @staticmethod
    def generate_url_from_id(image_id):
        return URL_FORMAT.format(image_id=image_id)