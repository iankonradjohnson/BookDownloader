from python.src.downloader.batch_archive_pdf_downloader import BatchArchiveDownloader
from python.src.downloader.downloader import Downloader
from python.src.downloader.numbered_url_book_downloader import NumberedUrlBookDownloader
from python.src.generator.rara_url_generator import RaraUrlGenerator


class ImageDownloaderFactory:
    @staticmethod
    def create_downloader(config) -> Downloader:
        downloader_type = config.get("downloader_type")
        if downloader_type == "rara":
            return NumberedUrlBookDownloader(RaraUrlGenerator(config), config)
        elif downloader_type == "arachne":
            return NumberedUrlBookDownloader(RaraUrlGenerator(config), config)
        elif downloader_type == "batch_archive_zip":
            return BatchArchiveDownloader(config, download_type="PROCESSED_ZIP")
        elif downloader_type == "batch_archive_tar":
            return BatchArchiveDownloader(config, download_type="ORIGINAL_TAR")
