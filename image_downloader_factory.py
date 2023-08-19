from arachne_downloader import ArachneDownloader
from rara_downloader import RaraDownloader


class ImageDownloaderFactory:
    @staticmethod
    def create_downloader(config):
        downloader_type = config.get("downloader_type")
        if downloader_type == "rara":
            return RaraDownloader(config)
        elif downloader_type == "arachne":
            return ArachneDownloader(config)
