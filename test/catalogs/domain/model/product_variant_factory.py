import random
import uuid

from factory import BUILD_STRATEGY, lazy_attribute, Factory
from faker import Faker

from src.catalogs.domain.model.product_variant import ProductVariant

fake = Faker('pt_BR')


class ProductVariantFactory(Factory):
    class Meta:
        strategy = BUILD_STRATEGY
        model = ProductVariant

    id = lazy_attribute(lambda o: uuid.uuid4())
    name = lazy_attribute(lambda o: fake.name())
    description = lazy_attribute(lambda o: fake.text())
    price = lazy_attribute(lambda o: random.randint(100, 10000))
    image_key = lazy_attribute(lambda o: str(o.id))
