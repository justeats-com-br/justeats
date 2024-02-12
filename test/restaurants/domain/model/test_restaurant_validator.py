import pytest
from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.message import Message, MessageCategory
from src.infrastructure.storage.document_type_service import DocumentTypeService
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository
from src.restaurants.domain.model.restaurant_validator import RestaurantValidator
from test.infrastructure.common.message_test_util import text_for_key
from test.restaurants.domain.model.restaurant_factory import RestaurantFactory


class TestRestaurantValidator:
    @fixture
    def restaurant_repository(self) -> RestaurantRepository:
        restaurant_repository = MagicMock()
        restaurant_repository.load_by_document_number = MagicMock(return_value=None)
        return restaurant_repository

    @fixture
    def document_type_service(self) -> DocumentTypeService:
        document_type_service = MagicMock()
        document_type_service.load_image_type = MagicMock(return_value='image/png')
        return document_type_service

    @fixture
    def validator(self, restaurant_repository, document_type_service) -> RestaurantValidator:
        return RestaurantValidator(restaurant_repository, document_type_service)

    @fixture
    def logo(self) -> bytes:
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82'

    def test_category_should_be_required(self, validator, logo):
        restaurant = RestaurantFactory(category=None)

        messages = validator.validate_new_restaurant(restaurant, logo)

        expected_key = 'nullable'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='category',
            message=text_for_key(expected_key),
            key=expected_key
        )]

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_name_should_be_required(self, invalid_value, key, validator, logo):
        restaurant = RestaurantFactory(name=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=text_for_key(key),
            key=key
        )]

    def test_name_should_be_at_most_100_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(101))
        restaurant = RestaurantFactory(name=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=text_for_key(key),
            key=key,
            args=[100]
        )]

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_zip_code_should_be_required(self, invalid_value, key, validator, logo):
        restaurant = RestaurantFactory(address__zip_code=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='zip_code',
            message=text_for_key(key),
            key=key
        )]

    def test_zip_code_should_be_at_most_8_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(9))
        restaurant = RestaurantFactory(address__zip_code=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='zip_code',
            message=text_for_key(key),
            key=key,
            args=[8]
        )]

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_city_should_be_required(self, invalid_value, key, validator, logo):
        restaurant = RestaurantFactory(address__city=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='city',
            message=text_for_key(key),
            key=key
        )]

    def test_city_should_be_at_most_100_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(101))
        restaurant = RestaurantFactory(address__city=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='city',
            message=text_for_key(key),
            key=key,
            args=[100]
        )]

    def test_state_should_be_required(self, validator, logo):
        restaurant = RestaurantFactory(address__state=None)

        messages = validator.validate_new_restaurant(restaurant, logo)

        expected_key = 'nullable'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='state',
            message=text_for_key(expected_key),
            key=expected_key
        )]

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_street_should_be_required(self, invalid_value, key, validator, logo):
        restaurant = RestaurantFactory(address__street=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='street',
            message=text_for_key(key),
            key=key
        )]

    def test_street_should_be_at_most_200_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(201))
        restaurant = RestaurantFactory(address__street=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='street',
            message=text_for_key(key),
            key=key,
            args=[200]
        )]

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_number_should_be_required(self, invalid_value, key, validator, logo):
        restaurant = RestaurantFactory(address__number=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='number',
            message=text_for_key(key),
            key=key
        )]

    def test_number_should_be_at_most_20_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(21))
        restaurant = RestaurantFactory(address__number=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='number',
            message=text_for_key(key),
            key=key,
            args=[20]
        )]

    def test_complement_should_be_at_most_50_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(51))
        restaurant = RestaurantFactory(address__complement=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='complement',
            message=text_for_key(key),
            key=key,
            args=[50]
        )]

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_document_number_should_be_required(self, invalid_value, key, validator, logo):
        restaurant = RestaurantFactory(document_number=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='document_number',
            message=text_for_key(key),
            key=key
        )]

    def test_document_number_with_ponctuation_should_be_invalid(self, validator, logo):
        invalid_value = '47.315.184/0001-42'
        restaurant = RestaurantFactory(document_number=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        expected_key = 'invalid_document_number'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='document_number',
            message=text_for_key(expected_key),
            key=expected_key
        )]

    def test_document_number_with_same_number_should_be_invalid(self, validator, logo):
        invalid_value = '99999999999999'
        restaurant = RestaurantFactory(document_number=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        expected_key = 'invalid_document_number'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='document_number',
            message=text_for_key(expected_key),
            key=expected_key
        )]

    def test_document_number_already_in_use_should_be_invalid(self, validator, restaurant_repository, logo):
        invalid_value = '47315184000142'
        restaurant_repository.load_by_document_number = MagicMock(
            return_value=RestaurantFactory(document_number=invalid_value))
        restaurant = RestaurantFactory(document_number=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        expected_key = 'unique_document_number'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='document_number',
            message=text_for_key(expected_key),
            key=expected_key
        )]

    def test_document_number_with_valid_number_should_be_valid(self, validator, logo):
        invalid_value = '47315184000142'
        restaurant = RestaurantFactory(document_number=invalid_value)
        messages = validator.validate_new_restaurant(restaurant, logo)
        assert not messages

    def test_logo_should_be_a_valid_image_type(self, validator, document_type_service, logo):
        document_type_service.load_image_type = MagicMock(return_value=None)
        restaurant = RestaurantFactory()
        messages = validator.validate_new_restaurant(restaurant, logo)
        expected_key = 'invalid_image_type'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='logo',
            message=text_for_key(expected_key),
            key=expected_key
        )]

    def test_description_should_be_at_most_300_characters(self, validator, logo):
        big_text = "".join('a' for _ in range(301))
        restaurant = RestaurantFactory(description=big_text)
        messages = validator.validate_new_restaurant(restaurant, logo)
        key = 'maxlength'
        assert messages == [Message(
            category=MessageCategory.VALIDATION,
            target='description',
            message=text_for_key(key),
            key=key,
            args=[300]
        )]
