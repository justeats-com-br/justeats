from typing import List, Optional, Tuple

from src.catalogs.domain.model.modifier import Modifier
from src.catalogs.domain.model.modifier_validator import ModifierValidator
from src.catalogs.domain.model.product import Product
from src.catalogs.domain.model.product_repository import ProductRepository
from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message


class ModifierService:
    def __init__(self, product_repository: Optional[ProductRepository] = None,
                 modifier_validator: Optional[ModifierValidator] = None):
        self.product_repository = product_repository or ProductRepository()
        self.modifier_validator = modifier_validator or ModifierValidator()

    def add(self, product: Product, modifier: Modifier) -> Either[List[Message], Tuple[Product, Modifier]]:
        messages = self.modifier_validator.validate_new_modifier(modifier)
        if messages:
            return Left(messages)

        product.modifiers.append(modifier)
        self.product_repository.update(product)

        return Right((product, modifier))

    def update(self, product: Product, modifier_to_update: Modifier) -> Either[List[Message], Tuple[Product, Modifier]]:
        messages = self.modifier_validator.validate_update_modifier(modifier_to_update, product)
        if messages:
            return Left(messages)

        for i, modifier in enumerate(product.modifiers):
            if modifier.id == modifier_to_update.id:
                product.modifiers[i] = modifier_to_update
                break

        self.product_repository.update(product)

        return Right((product, modifier_to_update))
