from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlalchemy_utils import UUIDType

from src.catalogs.domain.model.catalog import Catalog
from src.infrastructure.common.domain_model import Base
from src.infrastructure.common.utils import tz_aware, tz_to_utc
from src.infrastructure.database.connection_factory import Session


class CatalogRepository:
    def __init__(self):
        self.session = Session()

    def add(self, catalog: Catalog) -> None:
        self.session.add(CatalogTable.to_table(catalog))

    def load_by_restaurant_id(self, restaurant_id: UUID) -> Optional[Catalog]:
        result = self.session.query(CatalogTable).filter(CatalogTable.restaurant_id == restaurant_id).first()
        return result.to_domain() if result else None

    def load(self, catalog_id: UUID) -> Optional[Catalog]:
        result = self.session.query(CatalogTable).filter(CatalogTable.id == catalog_id).first()
        return result.to_domain() if result else None


class CatalogTable(Base):
    __tablename__ = 'catalogs'
    id = Column(UUIDType(), primary_key=True)
    restaurant_id = Column(UUIDType(), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __init__(self, id: UUID, restaurant_id: UUID, created_at: DateTime, updated_at: DateTime):
        self.id = id
        self.restaurant_id = restaurant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def to_domain(self) -> Catalog:
        return Catalog(
            id=self.id,
            restaurant_id=self.restaurant_id,
            created_at=tz_aware(self.created_at),
            updated_at=tz_aware(self.updated_at)
        )

    @staticmethod
    def to_table(catalog) -> 'CatalogTable':
        return CatalogTable(
            id=catalog.id,
            restaurant_id=catalog.restaurant_id,
            created_at=tz_to_utc(catalog.created_at),
            updated_at=tz_to_utc(catalog.updated_at)
        )
