from gettext import gettext
from uuid import uuid4

from pytest import fixture

from src.infrastructure.common.message import Message, MessageCategory
from src.users.domain.service.auth_service import AuthService
from test.cognito_util import CognitoUtil
from test.integration_test import IntegrationTest


class TestAuthService(IntegrationTest):
    @fixture
    def cognito_util(self):
        return CognitoUtil()

    @fixture
    def auth_service(self):
        return AuthService()

    def test_should_invite_user(self, auth_service):
        email = '%s@blitsi.com.br' % str(uuid4())
        temp_password = auth_service._invite_user(email)
        assert temp_password

    def test_should_login_existing_user(self, cognito_util, auth_service):
        email = '%s@blitsi.com.br' % str(uuid4())
        password = 'Mypassword123456789@'
        cognito_util.create_confirmed_user(email, password)

        result = auth_service.login(email, password)

        assert result.is_right()
        (access_token, refresh_token) = result.right()
        assert access_token
        assert refresh_token

    def test_should_fail_on_wrong_password_for_login(self, cognito_util, auth_service):
        email = '%s@blitsi.com.br' % str(uuid4())
        password = 'Mypassword123456789@'
        cognito_util.create_confirmed_user(email, password)

        result = auth_service.login(email, 'wrongpassword12345')

        assert result.is_left()
        assert [Message(
            category=MessageCategory.VALIDATION,
            target='credentials',
            message=gettext('Wrong credentials'),
            key='wrong_credentials'
        )] == result.left()

    def test_should_fail_on_wrong_email_for_login(self, cognito_util, auth_service):
        email = '%s@blitsi.com.br' % str(uuid4())
        password = 'mypassword123456789'

        result = auth_service.login(email, password)

        assert result.is_left()
        assert [Message(
            category=MessageCategory.VALIDATION,
            target='credentials',
            message=gettext('Wrong credentials'),
            key='wrong_credentials'
        )] == result.left()

    def test_should_fail_on_first_login_required_for_login(self, cognito_util, auth_service):
        email = '%s@blitsi.com.br' % str(uuid4())
        temp_password = 'mypassword123456789'
        cognito_util.create_user(email, temp_password)

        result = auth_service.login(email, temp_password)

        assert result.is_left()
        assert [Message(
            category=MessageCategory.VALIDATION,
            target='password',
            message=gettext('First login required'),
            key='first_login_required'
        )] == result.left()

    def test_should_fail_on_wrong_password_for_first_login(self, cognito_util, auth_service):
        email = '%s@blitsi.com.br' % str(uuid4())
        temp_password = 'temp123456789'
        new_password = 'new123456789'
        cognito_util.create_user(email, temp_password)

        result = auth_service._first_login(email, 'wrong_credentials', new_password)

        assert result.is_left()
        assert [Message(
            category=MessageCategory.VALIDATION,
            target='credentials',
            message=gettext('Wrong credentials'),
            key='wrong_credentials'
        )] == result.left()
