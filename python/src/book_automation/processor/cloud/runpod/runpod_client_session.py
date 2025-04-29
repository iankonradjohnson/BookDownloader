import subprocess
import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from book_automation.externals.real_esrgan_client import RealESRGANClient
from book_automation.processor.cloud.file_uploader import FileUploader, SCPFileUploader


class RunPodClientSession:
    def __init__(self, 
                 pod_id: str,
                 client: RealESRGANClient,
                 file_uploader: FileUploader):
        self._pod_id = pod_id
        self._client = client
        self._file_uploader = file_uploader

    @property
    def client(self):
        return self._client

    @property
    def pod_id(self):
        return self._pod_id
        
    @property
    def file_uploader(self) -> FileUploader:
        return self._file_uploader
        
    @file_uploader.setter
    def file_uploader(self, uploader: FileUploader):
        self._file_uploader = uploader

    def upload_file(self, local_path: Path) -> str:
        return self._file_uploader.upload_file(local_path)

    def stop_pod(self):
        if self._pod_id:
            print(f"🛑 Stopping pod {self._pod_id}...")
            subprocess.run(["runpodctl", "stop", "pod", self._pod_id], check=True)

    def download_output_zip(self, download_url: str) -> Path:
        import tempfile
        from pathlib import Path

        tmp_download_dir = Path(tempfile.mkdtemp())
        output_zip_path = tmp_download_dir / "output.zip"

        self._client.download_output(download_url, output_dir=tmp_download_dir)
        print(f"✅ Output zip downloaded to {output_zip_path}")
        return output_zip_path

