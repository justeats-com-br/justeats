from datetime import datetime
from enum import Enum
from gettext import gettext
from typing import Optional, List
from uuid import UUID

from src.catalogs.domain.model.modifier import Modifier
from src.catalogs.domain.model.product_variant import ProductVariant
from src.infrastructure.common.domain_model import DomainModel


class Status(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

    def user_friendly_name(self):
        return {
            self.ACTIVE: gettext('Active'),
            self.INACTIVE: gettext('Inactive')
        }[self]


class Product(DomainModel):
    def __init__(self, id: UUID, section_id: UUID, name: str, description: Optional[str], price: Optional[int],
                 image_url: Optional[str], status: Status, variants: List[ProductVariant], modifiers: List[Modifier],
                 created_at: datetime, updated_at: datetime):
        self.id = id
        self.section_id = section_id
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url
        self.status = status
        self.variants = variants
        self.modifiers = modifiers
        self.created_at = created_at
        self.updated_at = updated_at
