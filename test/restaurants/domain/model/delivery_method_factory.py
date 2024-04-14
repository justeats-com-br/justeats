import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.infrastructure.database.connection_factory import Session
from src.restaurants.domain.model.delivery_method import DeliveryMethod, DeliveryType
from src.restaurants.domain.model.delivery_method_repository import DeliveryMethodTable

fake = Faker('pt_BR')


class DeliveryMethodFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = DeliveryMethod

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    delivery_type = lazy_attribute(lambda o: random.choice([delivery_type for delivery_type in DeliveryType]))
    delivery_radius = lazy_attribute(lambda o: random.randint(10, 50))
    delivery_fee = lazy_attribute(lambda o: random.randint(100, 10000))
    estimated_delivery_time = lazy_attribute(lambda o: random.randint(10, 90))


class DeliveryMethodTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = DeliveryMethodTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    delivery_type = lazy_attribute(lambda o: random.choice([delivery_type.value for delivery_type in DeliveryType]))
    delivery_radius = lazy_attribute(lambda o: random.randint(10, 50))
    delivery_fee = lazy_attribute(lambda o: random.randint(100, 10000))
    estimated_delivery_time = lazy_attribute(lambda o: random.randint(10, 90))
