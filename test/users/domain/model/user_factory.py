import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.infrastructure.database.connection_factory import Session
from src.users.domain.model.user import User, UserType
from src.users.domain.model.user_repository import UserTable

fake = Faker('pt_BR')


class UserFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = User

    id = lazy_attribute(lambda o: uuid.uuid4())
    email = lazy_attribute(lambda o: fake.company_email())
    name = lazy_attribute(lambda o: fake.name())
    type = lazy_attribute(lambda o: random.choice([type for type in UserType]))


class UserTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = UserTable
        sqlalchemy_session = Session

    id = lazy_attribute(lambda o: uuid.uuid4())
    email = lazy_attribute(lambda o: fake.company_email())
    name = lazy_attribute(lambda o: fake.name())
    type = lazy_attribute(lambda o: random.choice([type.value for type in UserType]))
