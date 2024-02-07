import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from faker import Faker

from src.infrastructure.common import DomainEvent, EventType
from test.users.domain.model.user_factory import UserFactory
from src.users.domain.model.user import User

fake = Faker('pt_BR')


class DomainEventFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = DomainEvent

    id = lazy_attribute(lambda o: uuid.uuid4())
    domain_name = lazy_attribute(lambda o: User.__class__.__name__)
    data = lazy_attribute(lambda o: UserFactory().__dict__)
    type = lazy_attribute(lambda o: random.choice([event_type for event_type in EventType]))
