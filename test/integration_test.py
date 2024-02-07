import boto3
import httpretty
import pytest
from moto import mock_sqs, mock_sns

from src.infrastructure.common.config import get_key
from src.infrastructure.database.connection_factory import Session


class IntegrationTest(object):
    @pytest.yield_fixture(scope="function", autouse=True)
    def session(self):
        yield Session()

        Session().rollback()
        Session.remove()

    @pytest.fixture(autouse=True)
    def sqs_client(self):
        sqs = mock_sqs()
        sqs.start()

        sqs_client = boto3.client(
            "sqs",
            region_name=get_key("AWS_REGION"),
            aws_access_key_id=get_key("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_key("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=get_key("AWS_SESSION_TOKEN"),
        )

        queues_env_vars = []
        for queue_env_var_name in queues_env_vars:
            queue_name = get_key(queue_env_var_name)
            staged_queue_name = f"test-{queue_name}"
            sqs_client.create_queue(QueueName=staged_queue_name)

        yield sqs_client

        sqs.stop()

    @pytest.fixture(autouse=True)
    def sns_client(self):
        sns = mock_sns()
        sns.start()

        sns_client = boto3.client(
            "sns",
            region_name=get_key("AWS_REGION"),
            aws_access_key_id=get_key("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_key("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=get_key("AWS_SESSION_TOKEN"),
        )
        topics_env_vars = [
        ]
        for topic_env_var in topics_env_vars:
            topic_name = get_key(topic_env_var).split(':')[-1].lower()
            sns_client.create_topic(Name=topic_name)

        yield sns_client

        sns.stop()

    @pytest.fixture(autouse=True)
    def configure_httpretty(self):
        httpretty.enable(verbose=True, allow_net_connect=False)
        yield
        httpretty.disable()
        httpretty.reset()
