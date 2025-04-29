import os
import requests
from dotenv import load_dotenv


class RunPodGraphQlClient:
    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("RUNPOD_API_KEY")
        if not self.api_key:
            raise EnvironmentError("RUNPOD_API_KEY is missing. Set it in your .env file.")

        self.endpoint = "https://api.runpod.io/graphql"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def get_pod_info(self, pod_id: str) -> dict:
        """
        Fetch detailed pod information including ports, gpus, container usage.
        """
        query = """
        query Pod {
          pod(input: {podId: "%s"}) {
            id
            name
            runtime {
              uptimeInSeconds
              ports {
                ip
                isIpPublic
                privatePort
                publicPort
                type
              }
              gpus {
                id
                gpuUtilPercent
                memoryUtilPercent
              }
              container {
                cpuPercent
                memoryPercent
              }
            }
          }
        }
        """ % pod_id
        variables = {}

        response = self.session.post(self.endpoint, json={"query": query, "variables": variables})

        if response.status_code != 200:
            raise Exception(f"RunPod API HTTP Error: {response.status_code}: {response.text}")

        result = response.json()
        if "errors" in result:
            raise Exception(f"RunPod API GraphQL Error: {result['errors']}")

        pod_data = result["data"]["pod"]
        if not pod_data:
            raise ValueError(f"No pod found with ID {pod_id}")

        return pod_data

    def get_pod_ssh_info(self, pod_id: str):
        """
        Fetch SSH connection details (public IP and public port for private port 22).
        """
        pod_info = self.get_pod_info(pod_id)
        ports = pod_info["runtime"]["ports"]

        ssh_port_info = next((port for port in ports if port["privatePort"] == 22), None)
        if not ssh_port_info:
            raise ValueError("No SSH port mapping found for this pod.")

        return {
            "ip": ssh_port_info["ip"],
            "port": ssh_port_info["publicPort"],
            "pod_name": pod_info["name"],
            "pod_id": pod_info["id"]
        }
