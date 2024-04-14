from mock import MagicMock
from pytest import fixture

from infrastructure.common.message import Message, MessageCategory
from payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository
from payments.domain.model.payment_receive_account_validator import PaymentReceiveAccountValidator
from test.payments.domain.model.payment_receive_account_factory import PaymentReceiveAccountFactory
from test.users.domain.model.user_factory import UserFactory
from users.domain.model.user import UserType


class TestPaymentReceiveAccountValidator:
    @fixture
    def payment_receive_account_repository(self) -> PaymentReceiveAccountRepository:
        return MagicMock()

    @fixture
    def validator(self, payment_receive_account_repository) -> PaymentReceiveAccountValidator:
        payment_receive_account_repository.load_by_content_creator_id = MagicMock(return_value=None)
        return PaymentReceiveAccountValidator(payment_receive_account_repository)

    def test_content_creator_type_should_be_allowed(self, validator):
        user = UserFactory(type=UserType.CONTENT_CREATOR)
        messages = validator.validate_user_for_new_account(user)
        assert not messages

    def test_fan_type_should_be_allowed(self, validator):
        user = UserFactory(type=UserType.FAN)
        messages = validator.validate_user_for_new_account(user)
        expected_messages = [Message(
            category=MessageCategory.VALIDATION,
            target='type',
            key='allowed',
            args=[UserType.CONTENT_CREATOR.value]
        )]
        assert messages == expected_messages

    def test_payment_receive_account_should_be_unique_per_user(self, payment_receive_account_repository, validator):
        user = UserFactory(type=UserType.CONTENT_CREATOR)
        payment_receive_account = PaymentReceiveAccountFactory(content_creator_id=user.id)
        payment_receive_account_repository.load_by_content_creator_id = MagicMock(return_value=payment_receive_account)
        messages = validator.validate_user_for_new_account(user)
        expected_messages = [Message(
            category=MessageCategory.VALIDATION,
            target='id',
            key='unique_payment_receive_account'
        )]
        assert messages == expected_messages
