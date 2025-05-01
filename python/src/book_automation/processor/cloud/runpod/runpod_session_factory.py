import os
import subprocess
import time
from enum import Enum, auto
from typing import Optional

import requests

from book_automation.externals.real_esrgan_client import RealESRGANClient
from book_automation.externals.runpod_gql_client import RunPodGraphQlClient
from book_automation.processor.cloud.file_uploader import SCPFileUploader, RunPodCtlFileUploader, \
    FileUploader
from book_automation.processor.cloud.runpod.runpod_client_session import (
    RunPodClientSession,
)


class FileUploadMethod(Enum):
    SCP = auto()
    RUNPODCTL = auto()


class RunPodClientSessionFactory:

    @staticmethod
    def create_session(
            pod_id: str = "r3wdkf9k23wbiz",
            container_port: int = 5000,
            upload_method: FileUploadMethod = FileUploadMethod.SCP,
            ssh_user: str = "root") -> RunPodClientSession:
        RunPodClientSessionFactory._launch_pod(pod_id)
        
        server_url = f"https://{pod_id}-{container_port}.proxy.runpod.net/"
        RunPodClientSessionFactory._wait_for_ready(server_url)
        print(f"🌍 Connected to server at {server_url}")
        client = RealESRGANClient(server_url)
        
        file_uploader: Optional[FileUploader] = None
        if upload_method == FileUploadMethod.SCP:
            # Get SSH info from RunPod GraphQL API
            gql_client = RunPodGraphQlClient()
            ssh_info = gql_client.get_pod_ssh_info(pod_id)
            ssh_host = ssh_info["ip"]
            ssh_port = str(ssh_info["port"])
            
            file_uploader = SCPFileUploader(host=ssh_host, port=ssh_port, user=ssh_user)
            print(f"📂 Using SCP file uploader with host {ssh_host}:{ssh_port}")
        elif upload_method == FileUploadMethod.RUNPODCTL:
            file_uploader = RunPodCtlFileUploader()
            print(f"📂 Using RunPodCtl file uploader")
        
        return RunPodClientSession(pod_id, client, file_uploader)

    @staticmethod
    def _launch_pod(pod_id: str):
        print("🚀 Launching RunPod...")
        subprocess.run([
            "runpodctl", "start", "pod", pod_id
        ])

    @staticmethod
    def _wait_for_ready(server_url):
        url = (server_url + "health")
        while requests.get(url).status_code != 200:
            time.sleep(5)

