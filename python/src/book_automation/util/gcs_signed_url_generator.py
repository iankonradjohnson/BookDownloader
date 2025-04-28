import os

from google.cloud import storage
from google.oauth2 import service_account

from datetime import timedelta


class GcsSignedUrlGenerator:

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GCS_CREDENTIALS_PATH"))
        self.client = storage.Client(credentials=credentials)

    def generate_signed_url(self, bucket_name, blob_name, expiration_minutes=60):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )

        return url
