import base64

import boto3

from src.infrastructure.common.config import get_key


class S3Client:
    def __init__(self, s3_client=None):
        self.s3_client = s3_client or boto3.client(
            "s3",
            region_name=get_key("AWS_REGION"),
            aws_access_key_id=get_key("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_key("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=get_key("AWS_SESSION_TOKEN"),
        )

    def put_base64_object(self, bucket_name: str, base_64_file: str, file_key: str, content_type: str) -> str:
        self.s3_client.put_object(
            Key=file_key,
            Body=base64.b64decode(base_64_file),
            Bucket=bucket_name,
            ContentType=content_type,
        )
        object_url = "http://{}.s3.amazonaws.com/{}".format(bucket_name, file_key)
        return object_url

    def put_binary_object(self, bucket_name: str, binary_file: bytes, file_key: str, content_type: str) -> str:
        self.s3_client.put_object(
            Key=file_key,
            Body=binary_file,
            Bucket=bucket_name,
            ContentType=content_type,
        )
        object_url = "http://{}.s3.amazonaws.com/{}".format(bucket_name, file_key)
        return object_url
