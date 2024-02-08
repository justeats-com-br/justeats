from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.domain_event import EventType
from src.infrastructure.common.either import Left, Right
from src.infrastructure.common.message import MessageCategory, Message
from src.infrastructure.topic.domain_event_notifier import DomainEventNotifier
from src.users.domain.model.user_repository import UserRepository
from src.users.domain.model.user_validator import UserValidator
from src.users.domain.service.auth_service import AuthService
from src.users.domain.service.user_service import UserService
from test.users.domain.model.user_factory import UserFactory


class TestUserService:
    @fixture
    def user_validator(self) -> UserValidator:
        return MagicMock()

    @fixture
    def user_repository(self) -> UserRepository:
        return MagicMock()

    @fixture
    def auth_service(self) -> AuthService:
        return MagicMock()

    @fixture
    def domain_event_notifier(self) -> DomainEventNotifier:
        return MagicMock()

    @fixture
    def user_service(self, user_validator, user_repository, auth_service, domain_event_notifier) -> UserService:
        return UserService(user_validator, user_repository, auth_service, domain_event_notifier)

    def test_sign_up_with_invalid_user_should_return_validation_messages(self, user_validator, user_service):
        invalid_user = UserFactory()
        password = 'someStrongPassword'
        validation_messages = [Message(
            category=MessageCategory.VALIDATION,
            target='invalid_email',
            message=gettext('Invalid email'),
            key='invalid_email'
        )]
        user_validator.validate_new_user = MagicMock(return_value=validation_messages)

        sign_up_result = user_service.sign_up(invalid_user, password)

        assert sign_up_result.is_left()
        assert sign_up_result.left() == validation_messages

    def test_sign_up_with_invalid_response_from_auth_service_should_not_add_user_and_return_validation_messages(self,
                                                                                                                user_validator,
                                                                                                                auth_service,
                                                                                                                user_repository,
                                                                                                                user_service):
        user = UserFactory()
        password = 'someStrongPassword'
        user_validator.validate_new_user = MagicMock(return_value=[])
        auth_service_messages = [Message(
            category=MessageCategory.VALIDATION,
            target='user',
            message=gettext('Some error in cognito'),
            key='some_error_in_cognito'
        )]
        auth_service.sign_up = MagicMock(return_value=Left(auth_service_messages))

        sign_up_result = user_service.sign_up(user, password)

        assert sign_up_result.is_left()
        assert sign_up_result.left() == auth_service_messages
        user_repository.add.assert_not_called()

    def test_sign_up_with_valid_user_should_return_signed_up_user(self, user_validator, user_repository, auth_service,
                                                                  domain_event_notifier, user_service):
        user = UserFactory()
        password = 'someStrongPassword'
        user_validator.validate_new_user = MagicMock(return_value=[])
        tokens = ('token', 'refresh_token')
        auth_service.sign_up = MagicMock(return_value=Right(tokens))

        sign_up_result = user_service.sign_up(user, password)

        assert sign_up_result.is_right()
        token, refresh_token = tokens
        assert sign_up_result.right() == (user, token, refresh_token)
        domain_event_notifier.notify_event.assert_called_once_with(user.id, user, EventType.ADDED)
