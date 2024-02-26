from typing import Optional
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class ProductVariant(DomainModel):
    def __init__(self, id: UUID, name: str, description: Optional[str], price: int, image_url: Optional[str]):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url
