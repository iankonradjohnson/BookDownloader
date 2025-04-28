import os
import shutil
import tempfile
import subprocess
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

from book_automation.processor.cloud.runpod.runpod_session_factory import RunPodClientSessionFactory
from book_automation.util.gcs_signed_url_generator import GcsSignedUrlGenerator

# Load environment variables from .env
load_dotenv()

class RunPodBatchRunner:
    def __init__(self,
                 input_dir: Path,
                 output_dir: Path,
                 gcs_bucket_name: str = "abacus-upscale-jobs",
                 container_port: int = 5000,
                 model_name: str = "net_g_1000000"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.gcs_bucket_name = gcs_bucket_name
        self.container_port = container_port
        self.model_name = model_name

        gcs_credentials_path = os.getenv("GCS_CREDENTIALS_PATH")
        if not gcs_credentials_path:
            raise ValueError("GCS_CREDENTIALS_PATH not set in .env file")
        self.gcs_credentials_path = Path(gcs_credentials_path)

    def run(self):
        print("🗜️ Zipping input directory...")
        tmp_zip_dir = Path(tempfile.mkdtemp())
        zip_name = self.input_dir.name + ".zip"
        input_zip = tmp_zip_dir / zip_name

        shutil.make_archive(
            input_zip.with_suffix('').as_posix(),
            'zip',
            root_dir=self.input_dir.parent,
            base_dir=self.input_dir.name
        )
        print(f"✅ Input zipped to {input_zip}")

        print("🚀 Uploading input zip to RunPod...")
        receive_code = self._send_zip_and_get_receive_code(input_zip)
        print(f"✅ Received code: {receive_code}")

        print("🚀 Creating RunPod session...")
        session = RunPodClientSessionFactory.create_session()

        try:
            client = session.client

            print("📝 Creating job...")
            job_id = client.create_job(
                receive_code=receive_code,
                model_name=self.model_name,
                gcs_credentials_path=self.gcs_credentials_path,
                gcs_bucket_name=self.gcs_bucket_name
            )
            print(f"✅ Job submitted: {job_id}")

            status = client.wait_for_completion(job_id)

            if status["status"] == "completed":
                print("📥 Downloading output...")
                download_url = GcsSignedUrlGenerator().generate_signed_url(self.gcs_bucket_name, f"jobs/{job_id}_out.zip")

                output_zip_path = session.download_output_zip(download_url)
                self._unzip_to_output(output_zip_path)
                self._delete_zip(output_zip_path)

                print(f"✅ Output downloaded to {self.output_dir}")
            else:
                print(f"❌ Job failed with error: {status.get('error')}")

        finally:
            print("🧹 Cleaning up: Stopping pod...")
            session.stop_pod()

    @staticmethod
    def _send_zip_and_get_receive_code(zip_path: Path) -> str:
        process = subprocess.Popen(
            ["runpodctl", "send", str(zip_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # line-buffered
        )

        receive_code = None

        def read_stdout():
            nonlocal receive_code
            for line in process.stdout:
                receive_code = line.strip()
                return

        # Start a thread to read stdout without blocking
        thread = threading.Thread(target=read_stdout)
        thread.start()

        # Give it a few seconds to *try* to get the receive code
        for _ in range(10):
            if receive_code:
                return receive_code
            time.sleep(0.5)

        raise RuntimeError("Failed to obtain receive code from runpodctl send output.")

    def _unzip_to_output(self, zip_path: Path):
        print(f"📂 Unzipping {zip_path} to {self.output_dir}...")
        time.sleep(5)
        shutil.unpack_archive(str(zip_path), extract_dir=str(self.output_dir))

    def _delete_zip(self, zip_path: Path):
        print(f"🗑️ Deleting temporary zip {zip_path}...")
        zip_path.unlink()

