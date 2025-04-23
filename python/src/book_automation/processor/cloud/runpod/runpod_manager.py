import subprocess
from pathlib import Path


class RunPodPodManager:
    def __init__(self, gpu_type: str = "NVIDIA GeForce RTX 4090", image_name: str = "iankonradjohnson/realesrgan-runpod:latest"):
        self.gpu_type = gpu_type
        self.image_name = image_name
        self.pod_id = None

    def launch_pod(self, name: str = "real-esrgan-job", gpu_count: int = 1, container_disk_size: int = 30) -> str:
        print("🚀 Launching RunPod...")
        
        result = subprocess.check_output([
            "runpodctl", "create", "pod", 
            "--gpuType", self.gpu_type,
            "--gpuCount", str(gpu_count),
            "--name", name,
            "--imageName", self.image_name,
            "--containerDiskSize", str(container_disk_size)
        ]).decode()
        # Output format: pod "67pxp7suorwgut" created for $0.340 / hr
        self.pod_id = result.strip().split('"')[1]
        print(f"🆔 Pod launched: {self.pod_id}")
        return self.pod_id

    def stop_pod(self):
        if self.pod_id:
            print("🧹 Stopping pod...")
            subprocess.run(["runpodctl", "stop", "pod", self.pod_id])

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
