import yaml
import sys
from factory.image_downloader_factory import ImageDownloaderFactory


def main():
    if len(sys.argv) != 2:
        print("Usage: python download_images.py <config_file>")
        return

    config_file = sys.argv[1]

    with open(config_file, 'r') as config_stream:
        config_data = yaml.safe_load(config_stream)

    downloader = ImageDownloaderFactory.create_downloader(config_data)
    downloader.download()


if __name__ == "__main__":
    main()
