import boto3
import httpretty
import pytest
from coverage.html import os
from moto import mock_sqs, mock_sns, mock_cognitoidp, mock_s3

from src.infrastructure.common.config import get_key
from src.infrastructure.database.connection_factory import Session


class IntegrationTest(object):
    @pytest.yield_fixture(scope="function", autouse=True)
    def session(self):
        yield Session()

        Session().rollback()
        Session.remove()

    @pytest.yield_fixture(scope="function", autouse=True)
    def cognito_client(self):
        idp = mock_cognitoidp()
        idp.start()

        cognito_client = boto3.client('cognito-idp',
                                      region_name=get_key('AWS_REGION'),
                                      aws_access_key_id=get_key('AWS_ACCESS_KEY_ID'),
                                      aws_secret_access_key=get_key('AWS_SECRET_ACCESS_KEY'),
                                      aws_session_token=get_key('AWS_SESSION_TOKEN'))

        # configure default users pool
        user_pool = cognito_client.create_user_pool(PoolName='users')
        os.environ['COGNITO_USER_POOL_ID'] = user_pool['UserPool']['Id']
        user_pool_client = cognito_client.create_user_pool_client(UserPoolId=user_pool['UserPool']['Id'],
                                                                  ClientName='test')
        os.environ['COGNITO_CLIENT_ID'] = user_pool_client['UserPoolClient']['ClientId']

        yield cognito_client

        del os.environ['COGNITO_USER_POOL_ID']
        del os.environ['COGNITO_CLIENT_ID']
        idp.stop()

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
            'DOMAIN_EVENTS_TOPIC'
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

    @pytest.fixture(autouse=True)
    def s3_client(self):
        s3 = mock_s3()
        s3.start()

        s3_client = boto3.client(
            "s3",
            region_name=get_key("AWS_REGION"),
            aws_access_key_id=get_key("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_key("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=get_key("AWS_SESSION_TOKEN"),
        )
        buckets_serverless = [
            "RESTAURANT_LOGO_BUCKET_NAME",
        ]

        for bucket_name in buckets_serverless:
            s3_client.create_bucket(
                Bucket=get_key(bucket_name)
            )

        yield s3_client

        s3.stop()
