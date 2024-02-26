from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, SmallInteger, String, DateTime
from sqlalchemy_utils import UUIDType

from src.catalogs.domain.model.section import Section
from src.infrastructure.common.domain_model import Base
from src.infrastructure.common.utils import tz_aware, tz_to_utc
from src.infrastructure.database.connection_factory import Session


class SectionRepository:
    def __init__(self):
        self.session = Session()

    def add(self, section: Section) -> None:
        self.session.add(SectionTable.to_table(section))

    def list_by_catalog_id(self, catalog_id: UUID) -> List[Section]:
        result = self.session.query(SectionTable).filter(SectionTable.catalog_id == catalog_id).all()
        return [record.to_domain() for record in result]

    def load(self, section_id: UUID) -> Optional[Section]:
        result = self.session.query(SectionTable).get(section_id)
        return result.to_domain() if result else None


class SectionTable(Base):
    __tablename__ = 'sections'
    id = Column(UUIDType(), primary_key=True)
    catalog_id = Column(UUIDType(), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    sort_order = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __init__(self, id: UUID, catalog_id: UUID, name: str, description: str, sort_order: int, created_at: DateTime,
                 updated_at: DateTime):
        self.id = id
        self.catalog_id = catalog_id
        self.name = name
        self.description = description
        self.sort_order = sort_order
        self.created_at = created_at
        self.updated_at = updated_at

    def to_domain(self) -> Section:
        return Section(
            id=self.id,
            catalog_id=self.catalog_id,
            name=self.name,
            description=self.description,
            sort_order=self.sort_order,
            created_at=tz_aware(self.created_at),
            updated_at=tz_aware(self.updated_at)
        )

    @staticmethod
    def to_table(section) -> 'SectionTable':
        return SectionTable(
            id=section.id,
            catalog_id=section.catalog_id,
            name=section.name,
            description=section.description,
            sort_order=section.sort_order,
            created_at=tz_to_utc(section.created_at),
            updated_at=tz_to_utc(section.updated_at)
        )
