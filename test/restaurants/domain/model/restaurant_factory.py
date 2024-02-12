import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.infrastructure.database.connection_factory import Session
from src.restaurants.domain.model.restaurant import Restaurant, Category, Address, State, Point
from src.restaurants.domain.model.restaurant_repository import RestaurantTable

fake = Faker('pt_BR')


class PointFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Point

    latitude = lazy_attribute(lambda o: fake.latitude())
    longitude = lazy_attribute(lambda o: fake.longitude())


class AddressFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Address

    street = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    number = lazy_attribute(lambda o: ''.join([str(random.randint(0, 9)) for _ in range(4)]))
    neighborhood = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    city = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    state = lazy_attribute(lambda o: random.choice([state for state in State]))
    zip_code = lazy_attribute(lambda o: ''.join([str(random.randint(0, 9)) for _ in range(8)]))
    complement = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    point = SubFactory(PointFactory)


class RestaurantFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Restaurant

    id = lazy_attribute(lambda o: uuid.uuid4())
    user_id = lazy_attribute(lambda o: uuid.uuid4())
    category = lazy_attribute(lambda o: random.choice([category for category in Category]))
    name = lazy_attribute(lambda o: fake.name())
    address = SubFactory(AddressFactory)
    document_number = lazy_attribute(lambda o: fake.cnpj().replace('.', '').replace('/', '').replace('-', ''))
    logo_url = lazy_attribute(lambda o: fake.image_url())
    description = lazy_attribute(lambda o: fake.text())


class RestaurantTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = RestaurantTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    user_id = lazy_attribute(lambda o: uuid.uuid4())
    category = lazy_attribute(lambda o: random.choice([category.value for category in Category]))
    name = lazy_attribute(lambda o: fake.name())
    address_street = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    address_number = lazy_attribute(lambda o: ''.join([str(random.randint(0, 9)) for _ in range(4)]))
    address_neighborhood = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    address_city = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    address_state = lazy_attribute(lambda o: random.choice([state.value for state in State]))
    address_zip_code = lazy_attribute(lambda o: ''.join([str(random.randint(0, 9)) for _ in range(8)]))
    address_complement = lazy_attribute(lambda o: fake.text(max_nb_chars=20))
    address_latitude = lazy_attribute(lambda o: fake.latitude())
    address_longitude = lazy_attribute(lambda o: fake.longitude())
    document_number = lazy_attribute(lambda o: fake.cnpj().replace('.', '').replace('/', '').replace('-', ''))
    logo_url = lazy_attribute(lambda o: fake.image_url())
    description = lazy_attribute(lambda o: fake.text())
