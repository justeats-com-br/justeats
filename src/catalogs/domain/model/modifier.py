from typing import Optional, List
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class ModifierOption(DomainModel):
    def __init__(self, id: UUID, name: str, description: Optional[str], price: Optional[int]):
        self.id = id
        self.name = name
        self.description = description
        self.price = price


class Modifier(DomainModel):
    def __init__(self, id: UUID, name: str, description: Optional[str], minimum_options: int,
                 maximum_options: int, options: List[ModifierOption]):
        self.id = id
        self.name = name
        self.description = description
        self.minimum_options = minimum_options
        self.maximum_options = maximum_options
        self.options = options
