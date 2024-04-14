import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from src.infrastructure.common.utils import get_utcnow
from src.infrastructure.database.connection_factory import Session
from src.payments.domain.model.payment_receive_account import PaymentReceiveAccount
from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountTable

fake = Faker('pt_BR')


class PaymentReceiveAccountFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = PaymentReceiveAccount

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    external_id = lazy_attribute(lambda o: str(uuid.uuid4()))
    created_at = lazy_attribute(lambda o: get_utcnow())
    onboarding_completed = lazy_attribute(lambda o: fake.boolean())


class PaymentReceiveAccountTableFactory(SQLAlchemyModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = PaymentReceiveAccountTable
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    id = lazy_attribute(lambda o: uuid.uuid4())
    restaurant_id = lazy_attribute(lambda o: uuid.uuid4())
    external_id = lazy_attribute(lambda o: str(uuid.uuid4()))
    created_at = lazy_attribute(lambda o: get_utcnow())
    onboarding_completed = lazy_attribute(lambda o: fake.boolean())
