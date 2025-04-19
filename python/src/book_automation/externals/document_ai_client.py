# working_document_ai_client.py

import os
import io
from dotenv import load_dotenv
from PIL import Image

from google.api_core.client_options import ClientOptions
from google.cloud.documentai_v1 import DocumentProcessorServiceClient
from google.cloud.documentai_v1.types import RawDocument, ProcessRequest, Document

from book_automation.processor.converter.pil_image_converter import PilImageConverter

load_dotenv()


def convert_image_to_pdf(image: Image.Image) -> bytes:
    pdf_bytes_io = io.BytesIO()
    image.save(pdf_bytes_io, format="PDF")
    return pdf_bytes_io.getvalue()


class DocumentAIClient:
    def __init__(self):
        self.project_id = os.environ["GCP_PROJECT_ID"]
        self.location = os.environ["GCP_LOCATION"]
        self.processor_id = os.environ["GCP_PROCESSOR_ID"]

        api_endpoint = f"{self.location}-documentai.googleapis.com"
        self.client = DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=api_endpoint)
        )

        self.name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"

    def process_image(self, image: Image.Image) -> Document:
        pdf_bytes = convert_image_to_pdf(image)
        raw_document = RawDocument(content=pdf_bytes, mime_type="application/pdf")
        request = ProcessRequest(name=self.name, raw_document=raw_document)
        result = self.client.process_document(request=request)
        return result.document
