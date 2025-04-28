import os
import shutil
import tempfile
from pathlib import Path


class ArchiveManager:
    @staticmethod
    def zip_directory(source_dir: Path, zip_name: str = "input_batch.zip") -> Path:
        print(f"Zipping {source_dir} to {zip_name}")
        zip_path = Path(tempfile.gettempdir()) / zip_name
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', source_dir)
        return zip_path

    @staticmethod
    def unzip_archive(zip_file: Path, extract_to: Path):
        shutil.unpack_archive(zip_file, extract_to)
        os.remove(zip_file)
