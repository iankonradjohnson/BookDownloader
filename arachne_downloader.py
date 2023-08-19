from image_downloader import ImageDownloader


class ArachneDownloader(ImageDownloader):

    def __init__(self, config):
        super().__init__(config.get("num_pages"), config.get("output_path"))
        self.start_id = config.get("start_id")
        self.book_id = config.get("book_id")

    def generate_url(self, page_num):
        return f"https://arachne.uni-koeln.de/arachne/images/image.php?file=BOOK-" \
               f"{self.book_id}-{str.zfill(str(page_num), 4)}_{self.start_id + page_num}.jpg"
