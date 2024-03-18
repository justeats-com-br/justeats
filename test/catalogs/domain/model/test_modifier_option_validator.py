import uuid
from typing import Optional
from uuid import UUID

import pytest
from pytest import fixture

from src.catalogs.domain.model.modifier import ModifierOption
from src.catalogs.domain.model.modifier_option_validator import ModifierOptionValidator
from src.catalogs.domain.model.product import Product
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.modifier_factory import ModifierOptionFactory
from test.catalogs.domain.model.product_factory import ProductFactory
from test.infrastructure.common.message_test_util import text_for_key


class TestModifierOptionValidator:
    @fixture
    def validator(self):
        return ModifierOptionValidator()

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_name_should_be_required(self, validator, invalid_value, key):
        option = ModifierOptionFactory(name=invalid_value)
        expected_message = Message(category=MessageCategory.VALIDATION, target='name', message=text_for_key(key),
                                   key=key)
        self._validate_modifier_option_and_expect_message(validator, option, expected_message)

    def test_name_should_be_at_most_100_characters(self, validator):
        big_text = "".join('a' for _ in range(101))
        option = ModifierOptionFactory(name=big_text)
        key = 'maxlength'
        expected_message = Message(category=MessageCategory.VALIDATION, target='name', message=text_for_key(key),
                                   key=key, args=[100])
        self._validate_modifier_option_and_expect_message(validator, option, expected_message)

    def test_description_should_be_optional(self, validator):
        option = ModifierOptionFactory(description=None)
        self._validate_modifier_option_and_expect_message(validator, option)

    def test_description_should_be_at_most_300_characters(self, validator):
        big_text = "".join('a' for _ in range(301))
        option = ModifierOptionFactory(description=big_text)
        expected_message = Message(category=MessageCategory.VALIDATION, target='description',
                                   message=text_for_key('maxlength'), key='maxlength', args=[300])
        self._validate_modifier_option_and_expect_message(validator, option, expected_message)

    def test_price_should_be_required(self, validator):
        option = ModifierOptionFactory(price=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='price',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_modifier_option_and_expect_message(validator, option, expected_message)

    def test_price_should_be_at_least_0(self, validator):
        option = ModifierOptionFactory(price=0)
        self._validate_modifier_option_and_expect_message(validator, option)

    def test_id_should_be_invalid_when_id_not_found_for_update(self, validator):
        option = ModifierOptionFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='id',
                                   message=text_for_key('invalid_id'), key='invalid_id')
        product = ProductFactory()
        messages = validator.validate_update_option(product, product.modifiers[0].id, option)
        assert messages == [expected_message]

    def test_modifier_id_should_be_invalid_when_id_not_found_for_update(self, validator):
        option = ModifierOptionFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='modifier_id',
                                   message=text_for_key('invalid_modifier_id'), key='invalid_modifier_id')
        product = ProductFactory()
        modifier_id = uuid.uuid4()
        messages = validator.validate_update_option(product, modifier_id, option)
        assert messages == [expected_message]

    def _validate_modifier_option_and_expect_message(self, validator: ModifierOptionValidator, option: ModifierOption,
                                                     expected_message: Optional[Message] = None,
                                                     product: Optional[Product] = None,
                                                     modifier_id: Optional[UUID] = None) -> None:
        messages = validator.validate_new_option(option)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages

        if not product and not modifier_id:
            product = ProductFactory()
            modifier_id = product.modifiers[0].id
            product.modifiers[0].options = [option]
        messages = validator.validate_update_option(product, modifier_id, option)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages
