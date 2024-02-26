from typing import List, Optional

from src.catalogs.domain.model.section import Section
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.model.section_validator import SectionValidator
from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message


class SectionService:
    def __init__(self, section_validator: Optional[SectionValidator] = None,
                 section_repository: Optional[SectionRepository] = None):
        self.section_validator = section_validator or SectionValidator()
        self.section_repository = section_repository or SectionRepository()

    def add(self, section: Section) -> Either[List[Message], Section]:
        messages = self.section_validator.validate_new_section(section)
        if messages:
            return Left(messages)

        self.section_repository.add(section)
        return Right(section)
