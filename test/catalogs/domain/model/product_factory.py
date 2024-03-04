import json
import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.catalogs.domain.model.product import Product, Status
from src.catalogs.domain.model.product_repository import ProductTable
from src.infrastructure.common.utils import get_utcnow
from src.infrastructure.database.connection_factory import Session
from src.infrastructure.serialization.object_json_encoder import ObjectJsonEncoder
from test.catalogs.domain.model.modifier_factory import ModifierFactory
from test.catalogs.domain.model.product_variant_factory import ProductVariantFactory

fake = Faker('pt_BR')


class ProductFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Product

    id = lazy_attribute(lambda o: uuid.uuid4())
    section_id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    price = lazy_attribute(lambda o: random.randint(100, 10000))
    image_key = lazy_attribute(lambda o: str(o.id))
    status = lazy_attribute(lambda o: random.choice([status for status in Status]))
    variants = lazy_attribute(lambda o: [ProductVariantFactory() for _ in range(3)])
    modifiers = lazy_attribute(lambda o: [ModifierFactory() for _ in range(3)])
    created_at = lazy_attribute(lambda o: get_utcnow())
    updated_at = lazy_attribute(lambda o: get_utcnow())


class ProductTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = ProductTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    section_id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    price = lazy_attribute(lambda o: random.randint(100, 10000))
    image_key = lazy_attribute(lambda o: str(o.id))
    status = lazy_attribute(lambda o: random.choice([status.value for status in Status]))
    variants = lazy_attribute(lambda o: json.dumps([ProductVariantFactory() for _ in range(3)], cls=ObjectJsonEncoder))
    modifiers = lazy_attribute(lambda o: json.dumps([ModifierFactory() for _ in range(3)], cls=ObjectJsonEncoder))
    created_at = lazy_attribute(lambda o: get_utcnow())
    updated_at = lazy_attribute(lambda o: get_utcnow())
