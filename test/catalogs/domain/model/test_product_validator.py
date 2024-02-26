from typing import Optional

import pytest
from mock import MagicMock
from pytest import fixture

from src.catalogs.domain.model.product import Status, Product
from src.catalogs.domain.model.product_validator import ProductValidator
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.product_factory import ProductFactory
from test.catalogs.domain.model.section_factory import SectionFactory
from test.infrastructure.common.message_test_util import text_for_key


class TestProductValidator:
    @fixture
    def section_repository(self):
        section_repository = MagicMock()
        section_repository.load = MagicMock(return_value=SectionFactory())
        return section_repository

    @fixture
    def document_type_service(self):
        document_type_service = MagicMock()
        document_type_service.load_image_type = MagicMock(return_value='image/png')
        return document_type_service

    @fixture
    def product_repository(self):
        product_repository = MagicMock()
        product_repository.load = MagicMock(return_value=ProductFactory())
        return product_repository

    @fixture
    def validator(self, section_repository, document_type_service, product_repository):
        return ProductValidator(section_repository, document_type_service, product_repository)

    @fixture
    def image(self) -> bytes:
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82'

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_section_id_should_be_required(self, validator, section_repository, invalid_value, key, image):
        product = ProductFactory(section_id=invalid_value)
        expected_message = Message(category=MessageCategory.VALIDATION, target='section_id', message=text_for_key(key),
                                   key=key)
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_section_id_should_be_invalid_when_id_not_found(self, validator, section_repository, image):
        section_repository.load = MagicMock(return_value=None)
        product = ProductFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='section_id',
                                   message=text_for_key('invalid_section_id'), key='invalid_section_id')
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_name_should_be_required(self, validator, section_repository, invalid_value, key, image):
        product = ProductFactory(name=invalid_value)
        expected_message = Message(category=MessageCategory.VALIDATION, target='name', message=text_for_key(key),
                                   key=key)
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_name_should_be_at_most_100_characters(self, validator, image):
        big_text = "".join('a' for _ in range(101))
        product = ProductFactory(name=big_text)
        key = 'maxlength'
        expected_message = Message(category=MessageCategory.VALIDATION, target='name', message=text_for_key(key),
                                   key=key, args=[100])
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_description_should_be_optional(self, validator, image):
        product = ProductFactory(description=None)
        self._validate_product_and_expect_message(validator, product, image, None)
        messages = validator.validate_new_product(product, image)
        assert messages == []

    def test_description_should_be_at_most_300_characters(self, validator, image):
        big_text = "".join('a' for _ in range(301))
        product = ProductFactory(description=big_text)
        expected_message = Message(category=MessageCategory.VALIDATION, target='description',
                                   message=text_for_key('maxlength'), key='maxlength', args=[300])
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_price_should_be_required(self, validator, image):
        product = ProductFactory(price=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='price',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_price_should_be_at_least_1(self, validator, image):
        product = ProductFactory(price=0)
        expected_message = Message(category=MessageCategory.VALIDATION, target='price', message=text_for_key('min'),
                                   key='min', args=[1])
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_status_should_be_required(self, validator, image):
        product = ProductFactory(status=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='status',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_status_should_be_active_or_inactive(self, validator, image):
        product = ProductFactory(status='invalid')
        expected_message = Message(category=MessageCategory.VALIDATION, target='status',
                                   message=text_for_key('allowed'), key='allowed', args=[status for status in Status])
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_image_should_be_optional(self, validator):
        product = ProductFactory()
        self._validate_product_and_expect_message(validator, product, None, None)

    def test_image_should_be_invalid_when_type_not_found(self, validator, document_type_service, image):
        document_type_service.load_image_type = MagicMock(return_value=None)
        product = ProductFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='image',
                                   message=text_for_key('invalid_image_type'), key='invalid_image_type')
        self._validate_product_and_expect_message(validator, product, image, expected_message)

    def test_id_should_be_invalid_when_id_not_found_for_update(self, validator, product_repository, image):
        product_repository.load = MagicMock(return_value=None)
        product = ProductFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='id',
                                   message=text_for_key('invalid_id'), key='invalid_id')
        messages = validator.validate_update_product(product, image)
        assert messages == [expected_message]

    def _validate_product_and_expect_message(self, validator: ProductValidator, product: Product,
                                             image: Optional[bytes], expected_message: Optional[Message]) -> None:
        messages = validator.validate_new_product(product, image)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages
        messages = validator.validate_update_product(product, image)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages
