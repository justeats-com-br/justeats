from typing import List, Optional
from uuid import UUID

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.catalogs.domain.model.modifier import ModifierOption
from src.catalogs.domain.model.product import Product
from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper


class ModifierOptionValidations(Validator):
    def __init__(self, product: Optional[Product], modifier_id: Optional[UUID], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        self.modifier_id = modifier_id

    def _validate_invalid_modifier_id(self, constraint, field, value):
        if value and self.product and self.modifier_id:
            product_modifier = next(
                (modifier for modifier in self.product.modifiers if modifier.id == self.modifier_id), None)
            if not product_modifier:
                self._error(field, ErrorDefinition(0, 'invalid_modifier_id'))
                self.recent_error.constraint = None

    def _validate_invalid_id(self, constraint, field, value):
        if value and self.product and self.modifier_id:
            product_modifier = next(
                (modifier for modifier in self.product.modifiers if modifier.id == self.modifier_id), None)
            if product_modifier:
                modifier_option = [option for option in product_modifier.options if option.id == value]
                if not modifier_option:
                    self._error(field, ErrorDefinition(0, 'invalid_id'))
                    self.recent_error.constraint = None


validation_schema = {
    'name': {'required': True, 'empty': False, 'maxlength': 100},
    'description': {'required': False, 'nullable': True, 'empty': False, 'maxlength': 300},
    'price': {'required': True, 'empty': False, 'min': 0},
}


class ModifierOptionValidator:
    def validate_new_option(self, option: ModifierOption) -> List[Message]:
        new_modifier_option_validation_schema = {
            **validation_schema,
        }

        validator = ModifierOptionValidations(None, None, new_modifier_option_validation_schema, allow_unknown=False)
        validator.validate({
            'name': option.name,
            'description': option.description,
            'price': option.price,
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_option(self, product: Product, modifier_id: UUID, option: ModifierOption) -> List[Message]:
        update_modifier_option_validation_schema = {
            **validation_schema,
            'id': {'required': True, 'empty': False, 'invalid_id': True},
            'modifier_id': {'required': True, 'empty': False, 'invalid_modifier_id': True},
        }

        validator = ModifierOptionValidations(product, modifier_id, update_modifier_option_validation_schema,
                                              allow_unknown=False)
        validator.validate({
            'id': option.id,
            'modifier_id': modifier_id,
            'name': option.name,
            'description': option.description,
            'price': option.price,
        })
        return MessageMapper.to_messages(validator._errors)
