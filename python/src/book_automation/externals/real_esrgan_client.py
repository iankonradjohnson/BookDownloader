import json
import os
import subprocess
import time

import requests


class RealESRGANClient:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip("/")

    def create_job(self, input_filename, model_name, gcs_credentials_path, gcs_bucket_name):
        with open(gcs_credentials_path) as f:
            gcs_credentials_json = json.load(f)

        payload = {
            "input_filename": input_filename,
            "model_name": model_name,
            "gcs_credentials_json": gcs_credentials_json,
            "gcs_bucket_name": gcs_bucket_name
        }
        response = requests.post(f"{self.server_url}/jobs", json=payload)
        response.raise_for_status()
        return response.json()["job_id"]

    def get_job_status(self, job_id):
        response = requests.get(f"{self.server_url}/jobs/{job_id}/status")
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, job_id, poll_interval=10):
        print(f"Waiting for job {job_id} to complete...")
        while True:
            status = self.get_job_status(job_id)
            print(f"Status: {status['status']}")
            if status['status'] in ["completed", "error"]:
                return status
            time.sleep(poll_interval)

    def download_output(self, url, output_dir="./downloads") -> str:
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "output.zip")

        print(f"Downloading with aria2c to {output_file}...")
        subprocess.run([
            "aria2c", "--file-allocation=none", "-x", "16", "-s", "16",
            "-d", output_dir, "-o", "output.zip",
            url
        ], check=True)

        return output_file


