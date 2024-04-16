from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.message import Message, MessageCategory
from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository
from src.payments.domain.model.payment_receive_account_validator import PaymentReceiveAccountValidator
from test.payments.domain.model.payment_receive_account_factory import PaymentReceiveAccountFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantFactory


class TestPaymentReceiveAccountValidator:
    @fixture
    def payment_receive_account_repository(self) -> PaymentReceiveAccountRepository:
        return MagicMock()

    @fixture
    def validator(self, payment_receive_account_repository) -> PaymentReceiveAccountValidator:
        payment_receive_account_repository.load_by_content_creator_id = MagicMock(return_value=None)
        return PaymentReceiveAccountValidator(payment_receive_account_repository)

    def test_payment_receive_account_should_be_unique_per_user(self, payment_receive_account_repository, validator):
        restaurant = RestaurantFactory()
        payment_receive_account = PaymentReceiveAccountFactory(restaurant_id=restaurant.id)
        payment_receive_account_repository.load_by_content_creator_id = MagicMock(return_value=payment_receive_account)
        messages = validator.validate_restaurant_for_new_account(restaurant)
        expected_messages = [Message(
            category=MessageCategory.VALIDATION,
            target='id',
            message=gettext('Payment receive account already exists'),
            key='unique_payment_receive_account'
        )]
        assert messages == expected_messages
