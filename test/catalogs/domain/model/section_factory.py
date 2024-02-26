import uuid

from factory import BUILD_STRATEGY, Factory, lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.catalogs.domain.model.section import Section
from src.catalogs.domain.model.section_repository import SectionTable
from src.infrastructure.common.utils import get_utcnow
from src.infrastructure.database.connection_factory import Session

fake = Faker('pt_BR')


class SectionFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Section

    id = lazy_attribute(lambda o: uuid.uuid4())
    catalog_id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    sort_order = lazy_attribute(lambda o: fake.random_int())
    created_at = lazy_attribute(lambda o: get_utcnow())
    updated_at = lazy_attribute(lambda o: get_utcnow())


class SectionTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = SectionTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    catalog_id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    sort_order = lazy_attribute(lambda o: fake.random_int())
    created_at = lazy_attribute(lambda o: get_utcnow())
    updated_at = lazy_attribute(lambda o: get_utcnow())
