from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.catalogs.domain.model.modifier import Modifier
from src.catalogs.domain.model.product import Product
from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper


class ModifierValidations(Validator):
    def __init__(self, product: Optional[Product], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

    def _validate_invalid_id(self, constraint, field, value):
        if value and self.product:
            product_modifier = [modifier for modifier in self.product.modifiers if modifier.id == value]
            if not product_modifier:
                self._error(field, ErrorDefinition(0, 'invalid_id'))
                self.recent_error.constraint = None


validation_schema = {
    'name': {'required': True, 'empty': False, 'maxlength': 100},
    'description': {'required': False, 'nullable': True, 'empty': False, 'maxlength': 300},
    'minimum_options': {'required': True, 'empty': False, 'min': 0, 'max': 30},
    'maximum_options': {'required': True, 'empty': False, 'min': 0, 'max': 30},
}


class ModifierValidator:
    def validate_new_modifier(self, modifier: Modifier) -> List[Message]:
        new_modifier_validation_schema = {
            **validation_schema,
        }

        validator = ModifierValidations(None, new_modifier_validation_schema, allow_unknown=False)
        validator.validate({
            'name': modifier.name,
            'description': modifier.description,
            'minimum_options': modifier.minimum_options,
            'maximum_options': modifier.maximum_options,
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_modifier(self, modifier: Modifier, product: Product) -> List[Message]:
        update_modifier_validation_schema = {
            **validation_schema,
            'id': {'required': True, 'empty': False, 'invalid_id': True},
        }

        validator = ModifierValidations(product, update_modifier_validation_schema, allow_unknown=False)
        validator.validate({
            'id': modifier.id,
            'name': modifier.name,
            'description': modifier.description,
            'minimum_options': modifier.minimum_options,
            'maximum_options': modifier.maximum_options,
        })
        return MessageMapper.to_messages(validator._errors)
