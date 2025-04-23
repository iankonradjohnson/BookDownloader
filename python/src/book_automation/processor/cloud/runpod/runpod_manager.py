import subprocess
from pathlib import Path


class RunPodPodManager:
    def __init__(self, template_id: str = "YOUR_TEMPLATE_ID"):
        self.template_id = template_id
        self.pod_id = None

    def launch_pod(self, name: str = "real-esrgan-job") -> str:
        print("🚀 Launching RunPod from template...")
        result = subprocess.check_output([
            "runpodctl", "create", "--template-id", self.template_id, "--name", name
        ]).decode()
        self.pod_id = result.strip().split()[-1]
        print(f"🆔 Pod launched: {self.pod_id}")
        return self.pod_id

    def stop_pod(self):
        if self.pod_id:
            print("🧹 Stopping pod...")
            subprocess.run(["runpodctl", "stop", self.pod_id])

    @staticmethod
    def upload_file(file_path: Path) -> str:
        print(f"📤 Uploading {file_path} to RunPod...")
        code = (
            subprocess.check_output(["runpodctl", "send", str(file_path)])
            .decode().strip().split()[-1]
        )
        print(f"🔑 Upload code: {code}")
        return code

    @staticmethod
    def download_file(remote_file: str, local_dest: Path):
        print(f"📥 Downloading {remote_file} from RunPod...")
        code = subprocess.check_output(["runpodctl", "send", remote_file]).decode().strip().split()[
            -1]
        subprocess.run(["runpodctl", "receive", code, "--output", str(local_dest)])
