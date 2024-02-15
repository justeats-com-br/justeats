import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.infrastructure.common.utils import get_utcnow
from src.infrastructure.database.connection_factory import Session
from src.restaurants.domain.model.working_hour import WorkingHour
from src.restaurants.domain.model.working_hour_repository import WorkingHourTable

fake = Faker('pt_BR')


class WorkingHourFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = WorkingHour

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    day_of_week = lazy_attribute(lambda o: random.randint(1, 7))
    opening_time = lazy_attribute(lambda o: get_utcnow().time())
    closing_time = lazy_attribute(lambda o: get_utcnow().time())


class WorkingHourTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = WorkingHourTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    day_of_week = lazy_attribute(lambda o: random.randint(1, 7))
    opening_time = lazy_attribute(lambda o: get_utcnow().time())
    closing_time = lazy_attribute(lambda o: get_utcnow().time())
