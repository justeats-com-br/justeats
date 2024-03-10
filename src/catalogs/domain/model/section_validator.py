from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.catalogs.domain.model.section import Section
from src.catalogs.domain.model.section_repository import SectionRepository
from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper


class SectionValidations(Validator):
    def __init__(self, section_repository: SectionRepository, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section_repository = section_repository

    def _validate_invalid_id(self, constraint, field, value):
        if value:
            product = self.section_repository.load(value)
            if not product:
                self._error(field, ErrorDefinition(0, 'invalid_id'))
                self.recent_error.constraint = None


validation_schema = {
    'name': {'required': True, 'empty': False, 'maxlength': 100},
    'description': {'required': False, 'empty': False, 'nullable': True, 'maxlength': 300},
    'sort_order': {'required': True, 'empty': False, 'min': 1},
}


class SectionValidator:
    def __init__(self, section_repository: Optional[SectionRepository] = None):
        self.section_repository = section_repository or SectionRepository()

    def validate_new_section(self, section: Section) -> List[Message]:
        validator = SectionValidations(self.section_repository, validation_schema, allow_unknown=False)
        validator.validate({
            'name': section.name,
            'description': section.description,
            'sort_order': section.sort_order
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_section(self, section: Section) -> List[Message]:
        update_section_validation_schema = {
            **validation_schema,
            'id': {'required': True, 'empty': False, 'invalid_id': True},
        }
        validator = SectionValidations(self.section_repository, update_section_validation_schema, allow_unknown=False)
        validator.validate({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'sort_order': section.sort_order
        })
        return MessageMapper.to_messages(validator._errors)
