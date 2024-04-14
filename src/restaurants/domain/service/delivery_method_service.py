from typing import Optional, List

from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message
from src.restaurants.domain.model.delivery_method import DeliveryMethod
from src.restaurants.domain.model.delivery_method_repository import DeliveryMethodRepository
from src.restaurants.domain.model.delivery_method_validator import DeliveryMethodValidator


class DeliveryMethodService:
    def __init__(self, delivery_method_validator: Optional[DeliveryMethodValidator] = None,
                 delivery_method_repository: Optional[DeliveryMethodRepository] = None):
        self.delivery_method_validator = delivery_method_validator or DeliveryMethodValidator()
        self.delivery_method_repository = delivery_method_repository or DeliveryMethodRepository()

    def add(self, delivery_method: DeliveryMethod) -> Either[List[Message], DeliveryMethod]:
        messages = self.delivery_method_validator.validate_new_delivery_method(delivery_method)
        if messages:
            return Left(messages)

        self.delivery_method_repository.add(delivery_method)
        return Right(delivery_method)

    def update(self, delivery_method: DeliveryMethod) -> Either[List[Message], DeliveryMethod]:
        messages = self.delivery_method_validator.validate_update_delivery_method(delivery_method)
        if messages:
            return Left(messages)

        self.delivery_method_repository.update(delivery_method)
        return Right(delivery_method)
