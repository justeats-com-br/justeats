from typing import Optional

import pytest
from pytest import fixture

from src.catalogs.domain.model.modifier import Modifier
from src.catalogs.domain.model.modifier_validator import ModifierValidator
from src.catalogs.domain.model.product import Product
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.modifier_factory import ModifierFactory
from test.catalogs.domain.model.product_factory import ProductFactory
from test.infrastructure.common.message_test_util import text_for_key


class TestModifierValidator:
    @fixture
    def validator(self):
        return ModifierValidator()

    @pytest.mark.parametrize("invalid_value,key", [('', 'empty'), (None, 'nullable')])
    def test_name_should_be_required(self, validator, invalid_value, key):
        modifier = ModifierFactory(name=invalid_value)
        expected_message = Message(category=MessageCategory.VALIDATION, target='name', message=text_for_key(key),
                                   key=key)
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_name_should_be_at_most_100_characters(self, validator):
        big_text = "".join('a' for _ in range(101))
        modifier = ModifierFactory(name=big_text)
        key = 'maxlength'
        expected_message = Message(category=MessageCategory.VALIDATION, target='name', message=text_for_key(key),
                                   key=key, args=[100])
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_description_should_be_optional(self, validator):
        modifier = ModifierFactory(description=None)
        self._validate_modifier_and_expect_message(validator, modifier)
        messages = validator.validate_new_modifier(modifier)
        assert messages == []

    def test_description_should_be_at_most_300_characters(self, validator):
        big_text = "".join('a' for _ in range(301))
        modifier = ModifierFactory(description=big_text)
        expected_message = Message(category=MessageCategory.VALIDATION, target='description',
                                   message=text_for_key('maxlength'), key='maxlength', args=[300])
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_minimum_options_should_be_required(self, validator):
        modifier = ModifierFactory(minimum_options=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='minimum_options',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_minimum_options_should_be_at_least_0(self, validator):
        modifier = ModifierFactory(minimum_options=-1)
        expected_message = Message(category=MessageCategory.VALIDATION, target='minimum_options',
                                   message=text_for_key('min'),
                                   key='min', args=[0])
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_maximum_options_should_be_required(self, validator):
        modifier = ModifierFactory(maximum_options=None)
        expected_message = Message(category=MessageCategory.VALIDATION, target='maximum_options',
                                   message=text_for_key('nullable'), key='nullable')
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_maximum_options_should_be_at_least_0(self, validator):
        modifier = ModifierFactory(maximum_options=-1)
        expected_message = Message(category=MessageCategory.VALIDATION, target='maximum_options',
                                   message=text_for_key('min'),
                                   key='min', args=[0])
        self._validate_modifier_and_expect_message(validator, modifier, expected_message)

    def test_id_should_be_invalid_when_id_not_found_for_update(self, validator):
        product = ProductFactory()
        expected_message = Message(category=MessageCategory.VALIDATION, target='id',
                                   message=text_for_key('invalid_id'), key='invalid_id')
        modifier = ModifierFactory()
        messages = validator.validate_update_modifier(modifier, product)
        assert messages == [expected_message]

    def _validate_modifier_and_expect_message(self, validator: ModifierValidator, modifier: Modifier,
                                              expected_message: Optional[Message] = None,
                                              product: Optional[Product] = None) -> None:
        messages = validator.validate_new_modifier(modifier)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages

        product = product or ProductFactory(modifiers=[modifier])
        messages = validator.validate_update_modifier(modifier, product)
        if expected_message:
            assert messages == [expected_message]
        else:
            assert not messages
