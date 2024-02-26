import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from faker import Faker

from src.catalogs.domain.model.modifier import Modifier, ModifierOption

fake = Faker('pt_BR')


class ModifierOptionFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = ModifierOption

    id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    price = lazy_attribute(lambda o: random.randint(100, 10000))


class ModifierFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = Modifier

    id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    minimum_options = lazy_attribute(lambda o: random.randint(0, 3))
    maximum_options = lazy_attribute(lambda o: random.randint(1, 3))
    options = lazy_attribute(lambda o: [ModifierOptionFactory() for _ in range(3)])
