from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper
from src.restaurants.domain.model.delivery_method import DeliveryType, DeliveryMethod
from src.restaurants.domain.model.delivery_method_repository import DeliveryMethodRepository
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository


class DeliveryMethodValidations(Validator):
    def __init__(self, delivery_method_repository: DeliveryMethodRepository,
                 restaurant_repository: RestaurantRepository, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delivery_method_repository = delivery_method_repository
        self.restaurant_repository = restaurant_repository

    def _validate_invalid_id(self, constraint, field, value):
        if value:
            delivery_method = self.delivery_method_repository.load(value)
            if not delivery_method:
                self._error(field, ErrorDefinition(0, 'invalid_id'))
                self.recent_error.constraint = None

    def _validate_invalid_restaurant_id(self, constraint, field, value):
        if value:
            restaurant = self.restaurant_repository.load(value)
            if not restaurant:
                self._error(field, ErrorDefinition(0, 'invalid_restaurant_id'))
                self.recent_error.constraint = None

    def _validate_existing_delivery_type(self, constraint, field, value):
        if value:
            delivery_method = self.delivery_method_repository.load_by_restaurant_and_delivery_type(
                self.document['restaurant_id'], value)
            if delivery_method:
                self._error(field, ErrorDefinition(0, 'existing_delivery_type'))
                self.recent_error.constraint = None


validation_schema = {
    'restaurant_id': {'required': True, 'empty': False, 'invalid_restaurant_id': True},
    'delivery_radius': {'required': True, 'empty': False, 'min': 1},
    'delivery_fee': {'required': True, 'empty': False, 'min': 0},
    'estimated_delivery_time': {'required': True, 'empty': False, 'min': 1},
}


class DeliveryMethodValidator:
    def __init__(self, delivery_method_repository: Optional[DeliveryMethodRepository] = None,
                 restaurant_repository: Optional[RestaurantRepository] = None):
        self.delivery_method_repository = delivery_method_repository or DeliveryMethodRepository()
        self.restaurant_repository = restaurant_repository or RestaurantRepository()

    def validate_new_delivery_method(self, delivery_method: DeliveryMethod) -> List[Message]:
        new_delivery_method_validation_schema = {
            **validation_schema,
            'delivery_type': {'required': True, 'empty': False,
                              'allowed': [delivery_type for delivery_type in DeliveryType],
                              'existing_delivery_type': True},
        }

        validator = DeliveryMethodValidations(self.delivery_method_repository,
                                              self.restaurant_repository,
                                              new_delivery_method_validation_schema,
                                              allow_unknown=False)
        validator.validate({
            'restaurant_id': delivery_method.restaurant_id,
            'delivery_type': delivery_method.delivery_type,
            'delivery_radius': delivery_method.delivery_radius,
            'delivery_fee': delivery_method.delivery_fee,
            'estimated_delivery_time': delivery_method.estimated_delivery_time,
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_delivery_method(self, delivery_method: DeliveryMethod) -> List[Message]:
        update_delivery_method_validation_schema = {
            **validation_schema,
            'id': {'required': True, 'empty': False, 'invalid_id': True},
            'delivery_type': {'required': True, 'empty': False,
                              'allowed': [delivery_type for delivery_type in DeliveryType]},
        }
        validator = DeliveryMethodValidations(self.delivery_method_repository,
                                              self.restaurant_repository,
                                              update_delivery_method_validation_schema,
                                              allow_unknown=False)
        validator.validate({
            'id': delivery_method.id,
            'restaurant_id': delivery_method.restaurant_id,
            'delivery_type': delivery_method.delivery_type,
            'delivery_radius': delivery_method.delivery_radius,
            'delivery_fee': delivery_method.delivery_fee,
            'estimated_delivery_time': delivery_method.estimated_delivery_time,
        })
        return MessageMapper.to_messages(validator._errors)
