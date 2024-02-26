from datetime import datetime
from typing import Optional
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class Section(DomainModel):
    def __init__(self, id: UUID, catalog_id: UUID, name: str, description: Optional[str], sort_order: int,
                 created_at: datetime, updated_at: datetime):
        self.id = id
        self.catalog_id = catalog_id
        self.name = name
        self.description = description
        self.sort_order = sort_order
        self.created_at = created_at
        self.updated_at = updated_at
