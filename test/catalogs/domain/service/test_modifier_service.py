from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.catalogs.domain.service.modifier_service import ModifierService
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.modifier_factory import ModifierFactory
from test.catalogs.domain.model.product_factory import ProductFactory


class TestModifierService:
    @fixture
    def product_repository(self):
        return MagicMock()

    @fixture
    def modifier_validator(self):
        return MagicMock()

    @fixture
    def modifier_service(self, product_repository, modifier_validator):
        return ModifierService(product_repository, modifier_validator)

    def test_add_with_invalid_modifier_should_return_validation_messages(self, modifier_validator, modifier_service):
        product = ProductFactory()
        invalid_modifier = ModifierFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        modifier_validator.validate_new_modifier = MagicMock(return_value=messages)

        add_result = modifier_service.add(product, invalid_modifier)

        assert add_result.is_left()
        assert add_result.left() == messages

    def test_add_with_valid_modifier_should_return_modifier(self, modifier_validator, product_repository,
                                                            modifier_service):
        product = ProductFactory()
        modifier = ModifierFactory()
        modifier_validator.validate_new_modifier = MagicMock(return_value=[])

        add_result = modifier_service.add(product, modifier)

        assert add_result.is_right()
        assert add_result.right() == (product, modifier)
        assert modifier in product.modifiers
        product_repository.update.assert_called_once_with(product)

    def test_update_with_invalid_modifier_should_return_validation_messages(self, modifier_validator, modifier_service):
        product = ProductFactory()
        invalid_modifier = ModifierFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        modifier_validator.validate_update_modifier = MagicMock(return_value=messages)

        update_result = modifier_service.update(product, invalid_modifier)

        assert update_result.is_left()
        assert update_result.left() == messages

    def test_update_with_valid_modifier_should_return_modifier(self, modifier_validator, product_repository,
                                                               modifier_service):
        product = ProductFactory()
        modifier = product.modifiers[0]
        modifier.name = 'New name'
        modifier_validator.validate_update_modifier = MagicMock(return_value=[])

        update_result = modifier_service.update(product, modifier)

        assert update_result.is_right()
        assert update_result.right() == (product, modifier)
        assert modifier in product.modifiers
        product_repository.update.assert_called_once_with(product)
