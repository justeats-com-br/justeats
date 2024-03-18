from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.catalogs.domain.service.modifier_option_service import ModifierOptionService
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.modifier_factory import ModifierOptionFactory
from test.catalogs.domain.model.product_factory import ProductFactory


class TestModifierOptionService:
    @fixture
    def product_repository(self):
        return MagicMock()

    @fixture
    def modifier_option_validator(self):
        return MagicMock()

    @fixture
    def modifier_option_service(self, product_repository, modifier_option_validator):
        return ModifierOptionService(product_repository, modifier_option_validator)

    def test_add_with_invalid_modifier_option_should_return_validation_messages(self, modifier_option_validator,
                                                                                modifier_option_service):
        product = ProductFactory()
        modifier = product.modifiers[0]
        option = modifier.options[0]
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        modifier_option_validator.validate_new_option = MagicMock(return_value=messages)

        add_result = modifier_option_service.add(product, modifier.id, option)

        assert add_result.is_left()
        assert add_result.left() == messages

    def test_add_with_valid_modifier_option_should_return_product_modifier_and_option(self, modifier_option_validator,
                                                                                      product_repository,
                                                                                      modifier_option_service):
        product = ProductFactory()
        modifier = product.modifiers[0]
        option = modifier.options[0]
        option_to_update = ModifierOptionFactory(id=option.id)
        modifier_option_validator.validate_new_option = MagicMock(return_value=[])

        add_result = modifier_option_service.add(product, modifier.id, option_to_update)

        assert add_result.is_right()
        result_product, result_modifier, result_option = add_result.right()
        assert product == result_product
        assert modifier == result_modifier
        assert option_to_update == result_option
        assert option_to_update in result_modifier.options
        product_repository.update.assert_called_once_with(product)

    def test_update_with_invalid_modifier_option_should_return_validation_messages(self, modifier_option_validator,
                                                                                   modifier_option_service):
        product = ProductFactory()
        modifier = product.modifiers[0]
        option = modifier.options[0]
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        modifier_option_validator.validate_update_option = MagicMock(return_value=messages)

        update_result = modifier_option_service.update(product, modifier.id, option)

        assert update_result.is_left()
        assert update_result.left() == messages

    def test_update_with_valid_modifier_option_should_return_product_modifier_and_option(self,
                                                                                         modifier_option_validator,
                                                                                         product_repository,
                                                                                         modifier_option_service):
        product = ProductFactory()
        modifier = product.modifiers[0]
        option = modifier.options[0]
        option_to_update = ModifierOptionFactory(id=option.id)
        modifier_option_validator.validate_update_option = MagicMock(return_value=[])

        update_result = modifier_option_service.update(product, modifier.id, option_to_update)

        assert update_result.is_right()
        result_product, result_modifier, result_option = update_result.right()
        assert product == result_product
        assert modifier == result_modifier
        assert option_to_update == result_option
        assert option_to_update in result_modifier.options
        product_repository.update.assert_called_once_with(product)
