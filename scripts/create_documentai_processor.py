import os

from dotenv import load_dotenv
from google.cloud import documentai_v1beta3 as documentai

load_dotenv()

project_id = os.environ["GCP_PROJECT_ID"]
location = os.environ["GCP_LOCATION"]
processor_id = os.environ["GCP_PROCESSOR_ID"]

parent = f"projects/{project_id}/locations/{location}"


client = documentai.DocumentProcessorServiceClient()

processor = documentai.Processor(
    display_name="AbacusLayoutProcessor",
    type_="LAYOUT_PARSER_PROCESSOR"    # use whatever type you discovered above
)
response = client.create_processor(
    request={"parent": parent, "processor": processor}
)
print("Created:", response)

