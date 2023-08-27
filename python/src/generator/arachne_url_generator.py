from python.src.generator.url_generator import UrlGenerator


class ArachneGenerator(UrlGenerator):

    def __init__(self, start_id, book_id):
        self.start_id = start_id
        self.book_id = book_id

    def generate_url(self, page_num):
        return f"https://arachne.uni-koeln.de/arachne/images/image.php?file=BOOK-" \
               f"{self.book_id}-{str.zfill(str(page_num), 4)}_{self.start_id + page_num}.jpg"
