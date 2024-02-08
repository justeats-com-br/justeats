from enum import Enum
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class UserType(Enum):
    RESTAURANT_OWNER = 'RESTAURANT_OWNER'
    CUSTOMER = 'CUSTOMER'


class User(DomainModel):
    def __init__(self, id: UUID, email: str, name: str, type: UserType):
        self.id = id
        self.email = email
        self.name = name
        self.type = type
