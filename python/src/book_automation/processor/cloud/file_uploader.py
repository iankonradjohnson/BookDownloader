import subprocess
import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path


class FileUploader(ABC):
    @abstractmethod
    def upload_file(self, local_path: Path) -> str:
        pass


class SCPFileUploader(FileUploader):
    def __init__(self, host: str, port, user: str):
        self.host = host
        self.port = port
        self.user = user

    def upload_file(self, local_path: Path) -> str:
        remote_path = f"/workspace/{local_path.name}"

        print(f"📤 Uploading {local_path} to pod using SCP...")
        args = [
            "scp",
            "-P", self.port,
            "-i", "~/.ssh/id_ed25519",
            str(local_path),
            f"{self.user}@{self.host}:{remote_path}"
        ]
        print(" ".join(args))
        subprocess.run(args, check=True)

        print(f"✅ File uploaded to pod at {remote_path}")
        return remote_path


class RunPodCtlFileUploader(FileUploader):
    def upload_file(self, local_path: Path) -> str:
        process = subprocess.Popen(
            ["runpodctl", "send", str(local_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        receive_code = None

        def read_stdout():
            nonlocal receive_code
            for line in process.stdout:
                if "Code is:" in line:
                    receive_code = line.split("Code is:")[1].strip()
                    return

        thread = threading.Thread(target=read_stdout)
        thread.start()

        for _ in range(10):
            if receive_code:
                break
            time.sleep(0.5)

        if not receive_code:
            raise RuntimeError("Failed to obtain receive code from runpodctl send output.")

        print(f"✅ File uploaded with receive code: {receive_code}")
        return receive_code

