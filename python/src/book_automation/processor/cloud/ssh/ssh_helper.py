import os
import subprocess


class SSHHelper:
    def __init__(self, hostname: str, user: str, key_path: str = "~/.ssh/id_ed25519"):
        self.hostname = hostname
        self.user = user
        self.key_path = os.path.expanduser(key_path)

    def run(self, command: str):
        ssh_cmd = [
            "ssh",
            f"{self.user}@{self.hostname}",
            "-i", self.key_path,
            command
        ]
        return subprocess.run(ssh_cmd, check=True)