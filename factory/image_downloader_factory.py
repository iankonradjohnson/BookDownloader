from downloader.batch_archive_pdf_downloader import BatchArchivePdfDownloader
from downloader.downloader import Downloader
from downloader.numbered_url_book_downloader import NumberedUrlBookDownloader
from generator.rara_url_generator import RaraUrlGenerator


class ImageDownloaderFactory:
    @staticmethod
    def create_downloader(config) -> Downloader:
        downloader_type = config.get("downloader_type")
        if downloader_type == "rara":
            return NumberedUrlBookDownloader(RaraUrlGenerator(config), config)
        elif downloader_type == "arachne":
            return NumberedUrlBookDownloader(RaraUrlGenerator(config), config)
        elif downloader_type == "batch_archive_pdf":
            return BatchArchivePdfDownloader(config)
