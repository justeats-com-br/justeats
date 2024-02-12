from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper
from src.infrastructure.storage.document_type_service import DocumentTypeService
from src.restaurants.domain.model.restaurant import Restaurant
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository


def _calculate_cnpj_digit(cnpj, factor) -> str:
    sum = 0
    for digit in cnpj:
        if factor > 1:
            sum += int(digit) * factor
            factor -= 1
        if factor == 1:
            factor = 9
    mod = sum % 11
    return '0' if mod < 2 else str(11 - mod)


def _validate_cnpj(cnpj) -> bool:
    if len(cnpj) != 14:
        return False
    # Check if CNPJ is not a sequence of the same digit
    if cnpj == cnpj[0] * 14:
        return False
    # Calculate and validate first check digit
    first_check_digit = _calculate_cnpj_digit(cnpj[:12], 5)
    if first_check_digit != cnpj[12]:
        return False
    # Calculate and validate second check digit
    second_check_digit = _calculate_cnpj_digit(cnpj[:13], 6)
    if second_check_digit != cnpj[13]:
        return False

    return True


class RestaurantValidations(Validator):
    def __init__(self, restaurant_repository: RestaurantRepository, document_type_service: DocumentTypeService, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.restaurant_repository = restaurant_repository
        self.document_type_service = document_type_service

    def _validate_invalid_document_number(self, constraint, field, value):
        if value:
            if not _validate_cnpj(value):
                self._error(field, ErrorDefinition(0, 'invalid_document_number'))
                self.recent_error.constraint = None

    def _validate_unique_document_number(self, constraint, field, value):
        if value:
            found_restaurant = self.restaurant_repository.load_by_document_number(value)
            if found_restaurant:
                self._error(field, ErrorDefinition(0, 'unique_document_number'))
                self.recent_error.constraint = None

    def _validate_invalid_image_type(self, constraint, field, value):
        if value:
            image_type = self.document_type_service.load_image_type(value)
            if not image_type:
                self._error(field, ErrorDefinition(0, 'invalid_image_type'))
                self.recent_error.constraint = None


class RestaurantValidator:
    def __init__(self, restaurant_repository: Optional[RestaurantRepository] = None,
                 document_type_service: Optional[DocumentTypeService] = None):
        self.restaurant_repository = restaurant_repository or RestaurantRepository()
        self.document_type_service = document_type_service or DocumentTypeService()

    def validate_new_restaurant(self, restaurant: Restaurant, logo: bytes) -> List[Message]:
        validation_schema = {
            'category': {'required': True, 'empty': False},
            'name': {'required': True, 'empty': False, 'maxlength': 100},
            'zip_code': {'required': False, 'empty': False, 'maxlength': 8},
            'city': {'required': True, 'empty': False, 'maxlength': 100},
            'state': {'required': True, 'empty': False},
            'street': {'required': True, 'empty': False, 'maxlength': 200},
            'number': {'required': True, 'empty': False, 'maxlength': 20},
            'complement': {'required': False, 'empty': True, 'maxlength': 50},
            'document_number': {'required': True, 'empty': False, 'invalid_document_number': True,
                                'unique_document_number': True},
            'logo': {'required': False, 'invalid_image_type': True},
            'description': {'required': False, 'empty': False, 'maxlength': 300},
        }

        validator = RestaurantValidations(self.restaurant_repository, self.document_type_service, validation_schema,
                                          allow_unknown=False)
        validator.validate({
            'category': restaurant.category,
            'name': restaurant.name,
            'zip_code': restaurant.address.zip_code if restaurant.address else None,
            'city': restaurant.address.city if restaurant.address else None,
            'state': restaurant.address.state if restaurant.address else None,
            'street': restaurant.address.street if restaurant.address else None,
            'number': restaurant.address.number if restaurant.address else None,
            'complement': restaurant.address.complement if restaurant.address else None,
            'document_number': restaurant.document_number,
            'logo': logo,
            'description': restaurant.description,
        })
        return MessageMapper.to_messages(validator._errors)
