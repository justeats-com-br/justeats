from typing import Optional

import pytest
from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.message import Message, MessageCategory
from src.restaurants.domain.model.delivery_method import DeliveryMethod, DeliveryType
from src.restaurants.domain.model.delivery_method_validator import DeliveryMethodValidator
from test.infrastructure.common.message_test_util import text_for_key
from test.restaurants.domain.model.delivery_method_factory import DeliveryMethodFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantFactory


class TestDeliveryMethodValidator:
    @fixture
    def delivery_method_repository(self):
        delivery_method_repository = MagicMock()
        delivery_method_repository.load = MagicMock(return_value=DeliveryMethodFactory())
        delivery_method_repository.load_by_restaurant_and_delivery_type = MagicMock(return_value=None)
        return delivery_method_repository

    @fixture
    def restaurant_repository(self):
        restaurant_repository = MagicMock()
        restaurant_repository.load = MagicMock(return_value=RestaurantFactory())
        return restaurant_repository

    @fixture
    def validator(self, delivery_method_repository, restaurant_repository):
        return DeliveryMethodValidator(delivery_method_repository, restaurant_repository)

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_restaurant_id_should_be_required(self, validator, invalid_value, key):
        delivery_method = DeliveryMethodFactory(restaurant_id=invalid_value)
        expected_message = Message(category=MessageCategory.VALIDATION, target='restaurant_id',
                                   message=text_for_key(key),
                                   key=key)
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_restaurant_id_should_be_invalid_when_id_not_found(self, validator, restaurant_repository):
        restaurant_repository.load = MagicMock(return_value=None)
        delivery_method = DeliveryMethodFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='restaurant_id',
                                   message=text_for_key('invalid_restaurant_id'), key='invalid_restaurant_id')
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_type_should_be_required(self, validator):
        delivery_method = DeliveryMethodFactory(delivery_type=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_type',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_type_should_be_delivery_or_pickup(self, validator):
        delivery_method = DeliveryMethodFactory(delivery_type='invalid')
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_type',
                                   message=text_for_key('allowed'), key='allowed',
                                   args=[delivery_type for delivery_type in DeliveryType])
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_type_should_be_invalid_when_already_exists_for_restaurant(self, validator,
                                                                                delivery_method_repository):
        delivery_method_repository.load_by_restaurant_and_delivery_type = MagicMock(
            return_value=DeliveryMethodFactory())
        delivery_method = DeliveryMethodFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_type',
                                   message=text_for_key('existing_delivery_type'), key='existing_delivery_type')
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_radius_should_be_required(self, validator):
        delivery_method = DeliveryMethodFactory(delivery_radius=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_radius',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_radius_should_be_at_least_1(self, validator):
        delivery_method = DeliveryMethodFactory(delivery_radius=0)
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_radius',
                                   message=text_for_key('min'),
                                   key='min', args=[1])
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_fee_should_be_required(self, validator):
        delivery_method = DeliveryMethodFactory(delivery_fee=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_fee',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_delivery_fee_should_be_at_least_0(self, validator):
        delivery_method = DeliveryMethodFactory(delivery_fee=-1)
        expected_message = Message(category=MessageCategory.VALIDATION, target='delivery_fee',
                                   message=text_for_key('min'),
                                   key='min', args=[0])
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_estimated_delivery_time_should_be_required(self, validator):
        delivery_method = DeliveryMethodFactory(estimated_delivery_time=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='estimated_delivery_time',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_estimated_delivery_time_should_be_at_least_1(self, validator):
        delivery_method = DeliveryMethodFactory(estimated_delivery_time=0)
        expected_message = Message(category=MessageCategory.VALIDATION, target='estimated_delivery_time',
                                   message=text_for_key('min'),
                                   key='min', args=[1])
        self._validate_delivery_method_and_expect_message(validator, delivery_method, expected_message)

    def test_id_should_be_invalid_when_id_not_found_for_update(self, validator, delivery_method_repository):
        delivery_method_repository.load = MagicMock(return_value=None)
        delivery_method = DeliveryMethodFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='id',
                                   message=text_for_key('invalid_id'), key='invalid_id')
        messages = validator.validate_update_delivery_method(delivery_method)
        assert messages == [expected_message]

    def _validate_delivery_method_and_expect_message(self, validator: DeliveryMethodValidator,
                                                     delivery_method: DeliveryMethod,
                                                     expected_message: Optional[Message]) -> None:
        messages = validator.validate_new_delivery_method(delivery_method)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages
        messages = validator.validate_update_delivery_method(delivery_method)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages
