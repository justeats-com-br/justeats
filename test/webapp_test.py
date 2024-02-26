import os

from pytest import fixture

from src.restaurant_hub.app import create_app
from test.cognito_util import CognitoUtil
from test.integration_test import IntegrationTest
from test.users.domain.model.user_factory import UserTableFactory


class WebappTest(IntegrationTest):
    @fixture
    def logged_user_password(self):
        return 'SomeStrongPassword123@'

    @fixture
    def cognito_util(self):
        return CognitoUtil()

    @fixture
    def user(self):
        return UserTableFactory.create().to_domain()

    @fixture
    def cognito_user(self, cognito_client, cognito_util, logged_user_password, user):
        access_token, refresh_token = cognito_util.create_confirmed_user(user.email, logged_user_password)
        return user.email, access_token, refresh_token

    @fixture
    def logged_user(self, user, cognito_user, context, live_server):
        _, access_token, refresh_token = cognito_user
        context.add_cookies([
            {'name': 'access_token', 'value': access_token, 'url': live_server.url()},
            {'name': 'refresh_token', 'value': refresh_token, 'url': live_server.url()},
            {'name': 'email', 'value': user.email, 'url': live_server.url()},
        ])
        return user

    @fixture
    def app(self, cognito_user, sqs_client, sns_client, s3_client):
        os.environ['no_proxy'] = '*'
        app = create_app()
        app.config['SERVER_NAME'] = 'localhost'
        return app

    @fixture(autouse=True)
    def server(self, live_server):
        return live_server

    @fixture(autouse=True)
    def page_timeout(self, page):
        page.set_default_timeout(5000)
