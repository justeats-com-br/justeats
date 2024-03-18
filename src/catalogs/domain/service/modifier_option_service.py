from typing import Optional, List, Tuple
from uuid import UUID

from src.catalogs.domain.model.modifier import ModifierOption, Modifier
from src.catalogs.domain.model.modifier_option_validator import ModifierOptionValidator
from src.catalogs.domain.model.product import Product
from src.catalogs.domain.model.product_repository import ProductRepository
from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message


class ModifierOptionService:
    def __init__(self, product_repository: Optional[ProductRepository] = None,
                 modifier_option_validator: Optional[ModifierOptionValidator] = None):
        self.product_repository = product_repository or ProductRepository()
        self.modifier_option_validator = modifier_option_validator or ModifierOptionValidator()

    def add(self, product: Product, modifier_id: UUID, option: ModifierOption) -> Either[
        List[Message], Tuple[Product, Modifier, ModifierOption]]:
        messages = self.modifier_option_validator.validate_new_option(option)
        if messages:
            return Left(messages)

        modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
        modifier.options.append(option)
        self.product_repository.update(product)

        return Right((product, modifier, option))

    def update(self, product: Product, modifier_id: UUID, option: ModifierOption) -> Either[
        List[Message], Tuple[Product, Modifier, ModifierOption]]:
        messages = self.modifier_option_validator.validate_update_option(product, modifier_id, option)
        if messages:
            return Left(messages)

        modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
        option_index = next((i for i, o in enumerate(modifier.options) if o.id == option.id), None)
        modifier.options[option_index] = option
        self.product_repository.update(product)

        return Right((product, modifier, option))
