import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.catalogs.domain.model.catalog import Catalog
from src.catalogs.domain.model.catalog_repository import CatalogTable
from src.infrastructure.common.utils import get_utcnow
from src.infrastructure.database.connection_factory import Session

fake = Faker('pt_BR')


class CatalogFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Catalog

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    created_at = lazy_attribute(lambda o: get_utcnow())
    updated_at = lazy_attribute(lambda o: get_utcnow())


class CatalogTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = CatalogTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    created_at = lazy_attribute(lambda o: get_utcnow())
    updated_at = lazy_attribute(lambda o: get_utcnow())
