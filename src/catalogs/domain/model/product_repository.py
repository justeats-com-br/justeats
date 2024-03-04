import json
from typing import Optional, List
from uuid import UUID

from sqlalchemy import Column, DateTime, String, Integer, JSON
from sqlalchemy_utils import UUIDType

from src.catalogs.domain.model.modifier import Modifier, ModifierOption
from src.catalogs.domain.model.product import Product, Status
from src.catalogs.domain.model.product_variant import ProductVariant
from src.infrastructure.common.domain_model import Base
from src.infrastructure.common.utils import tz_aware, tz_to_utc
from src.infrastructure.database.connection_factory import Session
from src.infrastructure.serialization.object_json_encoder import ObjectJsonEncoder


class ProductRepository:
    def __init__(self):
        self.session = Session()

    def list_by_section_ids(self, section_ids: List[UUID]) -> List[Product]:
        result = self.session.query(ProductTable).filter(ProductTable.section_id.in_(section_ids)).all()
        return [record.to_domain() for record in result]

    def add(self, product: Product) -> None:
        self.session.add(ProductTable.to_table(product))

    def update(self, product: Product) -> None:
        self.session.merge(ProductTable.to_table(product))

    def load(self, product_id: UUID) -> Optional[Product]:
        result = self.session.query(ProductTable).filter(ProductTable.id == product_id).first()
        return result.to_domain() if result else None


class ProductTable(Base):
    __tablename__ = 'products'
    id = Column(UUIDType(), primary_key=True)
    section_id = Column(UUIDType(), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    image_key = Column(String, nullable=True)
    status = Column(String, nullable=False)
    variants = Column(JSON, nullable=False)
    modifiers = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __init__(self, id: UUID, section_id: UUID, name: str, description: Optional[str], price: Optional[int],
                 image_key: Optional[str], status: str, variants: json, modifiers: json, created_at: DateTime,
                 updated_at: DateTime):
        self.id = id
        self.section_id = section_id
        self.name = name
        self.description = description
        self.price = price
        self.image_key = image_key
        self.status = status
        self.variants = variants
        self.modifiers = modifiers
        self.created_at = created_at
        self.updated_at = updated_at

    def to_domain(self) -> Product:
        return Product(
            id=self.id,
            section_id=self.section_id,
            name=self.name,
            description=self.description,
            price=self.price,
            image_key=self.image_key,
            status=Status(self.status),
            variants=[self._to_variant_domain(record) for record in json.loads(self.variants)] if self.variants else [],
            modifiers=[self._to_modifier_domain(record) for record in
                       json.loads(self.modifiers)] if self.modifiers else [],
            created_at=tz_aware(self.created_at),
            updated_at=tz_aware(self.updated_at)
        )

    def _to_variant_domain(self, record: dict[str, any]) -> ProductVariant:
        return ProductVariant(
            id=UUID(record['id']),
            name=record['name'],
            description=record.get('description'),
            price=int(record['price']),
            image_key=record.get('image_key')
        )

    def _to_modifier_domain(self, record: dict[str, any]) -> Modifier:
        return Modifier(
            id=UUID(record['id']),
            name=record['name'],
            description=record.get('description'),
            minimum_options=int(record['minimum_options']),
            maximum_options=int(record['maximum_options']),
            options=[self._to_modifier_option(record) for record in record['options']]
        )

    def _to_modifier_option(self, record: dict[str, any]) -> ModifierOption:
        return ModifierOption(
            id=UUID(record['id']),
            name=record['name'],
            description=record.get('description'),
            price=int(record['price'])
        )

    @staticmethod
    def to_table(product) -> 'ProductTable':
        return ProductTable(
            id=product.id,
            section_id=product.section_id,
            name=product.name,
            description=product.description,
            price=product.price,
            image_key=product.image_key,
            status=product.status.value,
            variants=json.dumps(product.variants, cls=ObjectJsonEncoder),
            modifiers=json.dumps(product.modifiers, cls=ObjectJsonEncoder),
            created_at=tz_to_utc(product.created_at),
            updated_at=tz_to_utc(product.updated_at)
        )
