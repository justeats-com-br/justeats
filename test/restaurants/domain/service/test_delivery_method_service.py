from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.message import Message, MessageCategory
from src.restaurants.domain.model.delivery_method_repository import DeliveryMethodRepository
from src.restaurants.domain.model.delivery_method_validator import DeliveryMethodValidator
from src.restaurants.domain.service.delivery_method_service import DeliveryMethodService
from test.restaurants.domain.model.delivery_method_factory import DeliveryMethodFactory


class TestRestaurantService:
    @fixture
    def delivery_method_validator(self) -> DeliveryMethodValidator:
        return MagicMock()

    @fixture
    def delivery_method_repository(self) -> DeliveryMethodRepository:
        return MagicMock()

    @fixture
    def delivery_method_service(self, delivery_method_validator, delivery_method_repository) -> DeliveryMethodService:
        return DeliveryMethodService(delivery_method_validator, delivery_method_repository)

    def test_add_with_invalid_delivery_method_should_return_validation_messages(self, delivery_method_validator,
                                                                                delivery_method_service):
        invalid_delivery_method = DeliveryMethodFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='delivery_type',
            message=gettext('Required field'),
            key='empty'
        )]
        delivery_method_validator.validate_new_delivery_method = MagicMock(return_value=messages)

        add_result = delivery_method_service.add(invalid_delivery_method)

        assert add_result.is_left()
        assert add_result.left() == messages

    def test_add_with_valid_delivery_method_should_return_delivery_method(self, delivery_method_validator,
                                                                          delivery_method_repository,
                                                                          delivery_method_service):
        delivery_method = DeliveryMethodFactory()
        delivery_method_validator.validate_new_delivery_method = MagicMock(return_value=[])

        add_result = delivery_method_service.add(delivery_method)

        assert add_result.is_right()
        assert add_result.right() == delivery_method
        delivery_method_repository.add.assert_called_once_with(delivery_method)

    def test_update_with_invalid_delivery_method_should_return_validation_messages(self, delivery_method_validator,
                                                                                   delivery_method_service):
        invalid_delivery_method = DeliveryMethodFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='delivery_type',
            message=gettext('Required field'),
            key='empty'
        )]
        delivery_method_validator.validate_update_delivery_method = MagicMock(return_value=messages)

        update_result = delivery_method_service.update(invalid_delivery_method)

        assert update_result.is_left()
        assert update_result.left() == messages

    def test_update_with_valid_delivery_method_should_return_delivery_method(self, delivery_method_validator,
                                                                             delivery_method_repository,
                                                                             delivery_method_service):
        delivery_method = DeliveryMethodFactory()
        delivery_method_validator.validate_update_delivery_method = MagicMock(return_value=[])

        update_result = delivery_method_service.update(delivery_method)

        assert update_result.is_right()
        assert update_result.right() == delivery_method
        delivery_method_repository.update.assert_called_once_with(delivery_method)
