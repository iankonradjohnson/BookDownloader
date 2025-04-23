import os
from pathlib import Path

from book_automation.processor.cloud.cloud_batch_runner import CloudBatchRunner
from book_automation.processor.cloud.runpod.runpod_manager import RunPodPodManager
from book_automation.processor.cloud.ssh.ssh_helper import SSHHelper
from book_automation.processor.directory.image_directory_processor import ImageDirectoryProcessor
from book_automation.util.archive_manager import ArchiveManager


class RunPodBatchRunner(CloudBatchRunner):
    def __init__(self, input_dir: Path, output_dir: Path, image_directory_processor: ImageDirectoryProcessor):
        super().__init__(input_dir, output_dir, image_directory_processor)
        self.pod_manager = RunPodPodManager()
        self.ssh = None
        self.key_path = os.path.expanduser("~/.ssh/id_ed25519")

    def run(self):
        pod_id = self.pod_manager.launch_pod()
        self.ssh = SSHHelper(hostname="ssh.runpod.io", user=pod_id, key_path=self.key_path)

        input_zip = ArchiveManager.zip_directory(self.input_dir)
        code = self.pod_manager.upload_file(input_zip)

        print(f"📦 SSH into pod and receive file:")
        print(f"    runpodctl receive {code}")

        print("🧠 Running inference inside pod...")
        self.ssh.run("unzip input_batch.zip -d /workspace/input")
        self.ssh.run(self.processor.inference_command("/workspace/input", "/workspace/output"))
        self.ssh.run("zip -r output.zip /workspace/output")

        output_zip = self.output_dir / "output.zip"
        self.pod_manager.download_file("output.zip", output_zip)
        ArchiveManager.unzip_archive(output_zip, self.output_dir)
