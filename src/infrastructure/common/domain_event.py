from enum import Enum
from typing import Optional
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel
from src.infrastructure.common.utils import todict


class EventType(Enum):
    ADDED = 'ADDED'
    UPDATED = 'UPDATED'


class DomainEvent(DomainModel):
    def __init__(self, id: UUID, type: EventType, domain: Optional[DomainModel] = None, data: Optional[dict] = None,
                 domain_name: Optional[str] = None):
        self.id = id
        self.domain_name = domain_name or domain.__class__.__name__
        self.data = data or todict(domain)
        self.type = type
