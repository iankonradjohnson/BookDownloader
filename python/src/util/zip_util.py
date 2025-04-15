import os
import zipfile


class ZipUtil:

    @staticmethod
    def extract_zip(zip_path: str, extract_to: str):
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        print(f"Extracted {zip_path} to {extract_to}")