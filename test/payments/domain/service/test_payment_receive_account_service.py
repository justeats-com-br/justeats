from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.message import Message, MessageCategory
from src.payments.domain.service.payment_receive_account_service import PaymentReceiveAccountService
from test.restaurants.domain.model.restaurant_factory import RestaurantFactory


class TestPaymentReceiveAccountService:
    @fixture
    def payment_receive_account_validator(self):
        return MagicMock()

    @fixture
    def payment_receive_account_repository(self):
        return MagicMock()

    @fixture
    def stripe_client(self):
        return MagicMock()

    @fixture
    def payment_receive_account_service(self, payment_receive_account_validator, payment_receive_account_repository,
                                        stripe_client):
        return PaymentReceiveAccountService(payment_receive_account_validator, payment_receive_account_repository,
                                            stripe_client)

    def test_not_valid_user_should_return_message(self, payment_receive_account_validator,
                                                  payment_receive_account_repository,
                                                  payment_receive_account_service):
        validation_messages = [Message(
            category=MessageCategory.VALIDATION,
            message=gettext('Required field'),
            target='target',
            key='key'
        )]
        payment_receive_account_validator.validate_restaurant_for_new_account = MagicMock(
            return_value=validation_messages)
        restaurant = RestaurantFactory()
        return_url = 'return_url'
        refresh_url = 'refresh_url'
        payment_receive_account_repository.load_by_restaurant = MagicMock(return_value=None)

        result = payment_receive_account_service.add_for_restaurant(restaurant, return_url, refresh_url)

        assert result.is_left()
        assert result.left() == validation_messages

    def test_should_add_payment_receive_account(self, payment_receive_account_validator,
                                                payment_receive_account_repository,
                                                stripe_client, payment_receive_account_service):
        validation_messages = []
        payment_receive_account_validator.validate_restaurant_for_new_account = MagicMock(
            return_value=validation_messages)
        restaurant = RestaurantFactory()
        payment_receive_account_external_id = 'stripe_account_id'
        stripe_client.add_payment_receive_account_for_restaurant = MagicMock(
            return_value=payment_receive_account_external_id)
        onboarding_url = 'onboarding_url'
        stripe_client.generate_onboarding_url = MagicMock(return_value=onboarding_url)
        return_url = 'return_url'
        refresh_url = 'refresh_url'
        payment_receive_account_repository.load_by_restaurant = MagicMock(return_value=None)

        result = payment_receive_account_service.add_for_restaurant(restaurant, return_url, refresh_url)

        assert result.is_right()
        (added_payment_receive_account, result_onboarding_url) = result.right()
        assert result_onboarding_url == onboarding_url
        payment_receive_account_repository.add.assert_called_once_with(added_payment_receive_account)
        assert added_payment_receive_account.external_id == payment_receive_account_external_id
        assert added_payment_receive_account.restaurant_id == restaurant.id
        stripe_client.generate_onboarding_url.assert_called_once_with(added_payment_receive_account,
                                                                      return_url, refresh_url)
