from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String
from sqlalchemy_utils import UUIDType

from src.infrastructure.common.domain_model import Base
from src.infrastructure.database.connection_factory import Session
from src.users.domain.model.user import User, UserType


class UserRepository:
    def __init__(self):
        self.session = Session()

    def add(self, user: User) -> None:
        self.session.add(UserTable.to_table(user))

    def load_by_email(self, email: str) -> Optional[User]:
        result = self.session.query(UserTable).filter(UserTable.email == email).first()
        return result.to_domain() if result else None


class UserTable(Base):
    __tablename__ = 'users'
    id = Column(UUIDType(), primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    def __init__(self, id: UUID, email: str, name: str, type: str):
        self.id = id
        self.email = email
        self.name = name
        self.type = type

    def to_domain(self):
        return User(
            id=self.id,
            email=self.email,
            name=self.name,
            type=UserType(self.type),
        )

    @staticmethod
    def to_table(user):
        return UserTable(
            id=user.id,
            email=user.email,
            name=user.name,
            type=user.type.value,
        )
