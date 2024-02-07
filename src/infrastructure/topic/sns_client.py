import json
from collections import defaultdict
from typing import Tuple, Optional

import boto3

from src.infrastructure.common.config import get_key
from src.infrastructure.serialization.object_json_encoder import ObjectJsonEncoder


class SnsClient:
    def __init__(self, aws_sns_client=None):
        self.aws_sns_client = aws_sns_client or boto3.client(
            "sns",
            region_name=get_key("AWS_REGION"),
            aws_access_key_id=get_key("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_key("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=get_key("AWS_SESSION_TOKEN"),
        )

    def send_message(self, topic_arn, message, group_id=None):
        self.send_raw_message(topic_arn, json.dumps(message, cls=ObjectJsonEncoder), group_id)

    def send_raw_message(self, topic_arn, raw_message, group_id=None):
        pass
        # RequestSession.add_sns_message(topic_arn, raw_message, group_id)
        # messages = RequestSession.get_sns_messages()

    def flush_messages(self):
        sns_messages = list()
        messages_per_topic = defaultdict(list)
        for (topic_arn, json_string, group_id) in sns_messages:
            messages_per_topic[topic_arn].append((json_string, group_id))

        for topic_arn, messages in messages_per_topic.items():
            for message in messages:
                entry = self._build_entry(message)
                entry["TopicArn"] = topic_arn
                publish = self.aws_sns_client.publish(**entry)

    @staticmethod
    def _build_entry(message: Tuple[str, Optional[str]]) -> dict:
        json_string, group_id = message
        entry = {
            "Message": json_string,
        }
        return entry
