from typing import List

from cerberus import Validator

from src.catalogs.domain.model.section import Section
from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper


class SectionValidations(Validator):
    pass


class SectionValidator:
    def validate_new_section(self, section: Section) -> List[Message]:
        validation_schema = {
            'name': {'required': True, 'empty': False, 'maxlength': 100},
            'description': {'required': False, 'empty': False, 'nullable': True, 'maxlength': 300},
            'sort_order': {'required': True, 'empty': False, 'min': 1},
        }
        validator = SectionValidations(validation_schema, allow_unknown=False)
        validator.validate({
            'name': section.name,
            'description': section.description,
            'sort_order': section.sort_order
        })
        return MessageMapper.to_messages(validator._errors)
