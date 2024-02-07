import os

from pytest import fixture

from src.restaurant_hub.app import create_app
from test.cognito_util import CognitoUtil
from test.integration_test import IntegrationTest


class WebappTest(IntegrationTest):
    @fixture
    def logged_user_password(self):
        return 'SomeStrongPassword123@'

    @fixture
    def cognito_util(self):
        return CognitoUtil()

    @fixture
    def app(self, cognito_user, sqs_client, sns_client):
        os.environ['no_proxy'] = '*'
        app = create_app()
        app.config['SERVER_NAME'] = 'localhost'
        return app

    @fixture(autouse=True)
    def server(self, live_server):
        return live_server
