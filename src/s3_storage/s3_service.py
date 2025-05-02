import os
from io import BytesIO
from pathlib import Path

import boto3
from botocore.client import Config


class S3BucketService:
    def __init__(
            self,
            bucket_name: str,
            endpoint: str,
            access_key: str,
            secret_key: str
    ) -> None:
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def create_s3_client(self) -> boto3.client:
        client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4")
        )
        return client

    def upload_file_object(
            self,
            prefix: str,
            source_file_name: str,
            content: str | bytes
    ) -> None:
        client = self.create_s3_client()
        destination_path = str(Path(prefix, source_file_name))

        if isinstance(content, bytes):
            buffer = BytesIO(content)
        else:
            buffer = BytesIO(content.encode("utf-8"))
        client.upload_fileobj(buffer, self.bucket_name, destination_path)

    def delete_file_object(
            self,
            prefix: str,
            source_file_name: str
    ) -> None:
        client = self.create_s3_client()
        path_to_file = str(Path(prefix, source_file_name))
        client.delete_object(Bucket=self.bucket_name, key=path_to_file)

    def download_file_object(
            self,
            path: str,
            res_file: str
    ):
        path_to_file = str(Path(path))
        client = self.create_s3_client()
        # client.download_file(self.bucket_name, path, res_file)
        client.download_file(self.bucket_name, path_to_file, res_file)

def s3_bucket_service_factory() -> S3BucketService:
    return S3BucketService(
        bucket_name=os.getenv("BUCKET_NAME"),
        endpoint=os.getenv("ENDPOINT"),
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_KEY")
    )