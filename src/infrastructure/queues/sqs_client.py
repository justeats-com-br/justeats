import json
from collections import defaultdict
from typing import Tuple, Optional
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from src.infrastructure import chunks
from src.infrastructure.common.config import get_key
from src.infrastructure.serialization.object_json_encoder import ObjectJsonEncoder


class SqsClient:
    def __init__(self):
        self.aws_sqs_client = boto3.client(
            "sqs",
            region_name=get_key("AWS_REGION"),
            aws_access_key_id=get_key("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_key("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=get_key("AWS_SESSION_TOKEN"),
        )

    def send_message(self, queue_name, message, group_id=None):
        self._send_raw_message(queue_name, json.dumps(message, cls=ObjectJsonEncoder), group_id)

    def flush_messages(self):
        sqs_messages = list()
        if sqs_messages:
            messages_per_queue = defaultdict(list)
            for (queue_url, json_string, group_id) in sqs_messages:
                messages_per_queue[queue_url].append((json_string, group_id))

            for queue_url, queue_messages in messages_per_queue.items():
                entries = [
                    self._build_entry(queue_message) for queue_message in queue_messages
                ]
                for entries_batch in chunks(entries, 10):
                    self.aws_sqs_client.send_message_batch(
                        QueueUrl=queue_url, Entries=entries_batch
                    )

    def _send_raw_message(self, queue_name, raw_message, group_id=None):
        queue_url = self._get_queue_url(queue_name)
        # RequestSession.add_sqs_message(queue_url, raw_message, group_id)

    def _get_queue_url(self, queue_name):
        stage = get_key("STAGE")
        if ":" in queue_name:
            queue_name = self._get_queue_name(queue_name)
        staged_name = (
            queue_name
            if queue_name.startswith("dev-")
               or queue_name.startswith("test-")
               or queue_name.startswith("prod-")
            else f"{stage.lower()}-{queue_name}"
        )
        try:
            queue_url = self.aws_sqs_client.get_queue_url(QueueName=staged_name)[
                "QueueUrl"
            ]
            return queue_url
        except ClientError as e:
            if stage not in ("test", "prod"):
                return self.aws_sqs_client.get_queue_url(QueueName=f"dev-{queue_name}")[
                    "QueueUrl"
                ]
            else:
                raise e

    @staticmethod
    def _get_queue_name(queue_arn):
        return queue_arn[queue_arn.rfind(":") + 1: len(queue_arn)]

    @staticmethod
    def _build_entry(queue_message: Tuple[str, Optional[str]]) -> dict:
        json_string, group_id = queue_message
        if group_id:
            return dict(
                Id=uuid4().hex, MessageBody=json_string, MessageGroupId=group_id
            )
        else:
            return dict(Id=uuid4().hex, MessageBody=json_string)
