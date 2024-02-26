from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.catalogs.domain.service.section_service import SectionService
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.section_factory import SectionFactory


class TestSectionService:
    @fixture
    def section_validator(self):
        return MagicMock()

    @fixture
    def section_repository(self):
        return MagicMock()

    @fixture
    def section_service(self, section_validator, section_repository):
        return SectionService(section_validator, section_repository)

    def test_add_with_invalid_section_should_return_validation_messages(self, section_validator, section_service):
        invalid_section = SectionFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        section_validator.validate_new_section = MagicMock(return_value=messages)

        add_result = section_service.add(invalid_section)

        assert add_result.is_left()
        assert add_result.left() == messages

    def test_add_with_valid_section_should_return_section(self, section_validator, section_repository, section_service):
        section = SectionFactory()
        section_validator.validate_new_section = MagicMock(return_value=[])

        add_result = section_service.add(section)

        assert add_result.is_right()
        assert add_result.right() == section
        section_repository.add.assert_called_once_with(section)
