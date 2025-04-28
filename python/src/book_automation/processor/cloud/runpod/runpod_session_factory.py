import subprocess
import time

import requests

from book_automation.externals.real_esrgan_client import RealESRGANClient
from book_automation.processor.cloud.runpod.runpod_client_session import RunPodClientSession


class RunPodClientSessionFactory:

    @staticmethod
    def create_session(
            pod_id: str = "q38kd4z3fe6be7",
            container_port: int = 5000) -> RunPodClientSession:
        RunPodClientSessionFactory._launch_pod(pod_id)
        server_url = f"https://{pod_id}-{container_port}.proxy.runpod.net/"
        print(f"🌍 Connected to server at {server_url}")

        client = RealESRGANClient(server_url)

        return RunPodClientSession(pod_id, client)

    @staticmethod
    def _launch_pod(pod_id: str):
        print("🚀 Launching RunPod...")
        subprocess.run([
            "runpodctl", "start", "pod", pod_id
        ])

