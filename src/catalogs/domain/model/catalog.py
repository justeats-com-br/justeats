from datetime import datetime
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class Catalog(DomainModel):
    def __init__(self, id: UUID, restaurant_id: UUID, created_at: datetime, updated_at: datetime):
        self.id = id
        self.restaurant_id = restaurant_id
        self.created_at = created_at
        self.updated_at = updated_at
