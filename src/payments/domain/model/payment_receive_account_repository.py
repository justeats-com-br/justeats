from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy_utils import UUIDType

from src.infrastructure.common.domain_model import Base
from src.infrastructure.common.utils import tz_aware, tz_to_utc
from src.infrastructure.database.connection_factory import Session
from src.payments.domain.model.payment_receive_account import PaymentReceiveAccount


class PaymentReceiveAccountRepository:
    def __init__(self):
        self.session = Session()

    def add(self, payment_receive_account: PaymentReceiveAccount) -> None:
        self.session.add(PaymentReceiveAccountTable.to_table(payment_receive_account))

    def load_by_restaurant(self, restaurant_id: UUID) -> Optional[PaymentReceiveAccount]:
        result = self.session.query(PaymentReceiveAccountTable).filter(
            PaymentReceiveAccountTable.restaurant_id == restaurant_id).first()
        return result.to_domain() if result else None

    def load(self, id: UUID) -> Optional[PaymentReceiveAccount]:
        result = self.session.query(PaymentReceiveAccountTable).get(id)
        return result.to_domain() if result else None

    def load_by_external_id(self, external_id: str) -> Optional[PaymentReceiveAccount]:
        result = self.session.query(PaymentReceiveAccountTable).filter(
            PaymentReceiveAccountTable.external_id == external_id).first()
        return result.to_domain() if result else None

    def update(self, payment_receive_account: PaymentReceiveAccount) -> None:
        record = PaymentReceiveAccountTable.to_table(payment_receive_account)
        self.session.merge(record)


class PaymentReceiveAccountTable(Base):
    __tablename__ = 'payment_receive_accounts'
    id = Column(UUIDType(), nullable=False, primary_key=True)
    restaurant_id = Column(UUIDType(), nullable=False)
    external_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    onboarding_completed = Column(Boolean, nullable=False)

    def __init__(self, id: UUID, restaurant_id: UUID, external_id: str, created_at: datetime,
                 onboarding_completed: bool):
        self.id = id
        self.restaurant_id = restaurant_id
        self.external_id = external_id
        self.created_at = created_at
        self.onboarding_completed = onboarding_completed

    def to_domain(self) -> PaymentReceiveAccount:
        return PaymentReceiveAccount(
            id=self.id,
            restaurant_id=self.restaurant_id,
            external_id=self.external_id,
            created_at=tz_aware(self.created_at),
            onboarding_completed=self.onboarding_completed,
        )

    @staticmethod
    def to_table(payment_receive_account: PaymentReceiveAccount) -> 'PaymentReceiveAccountTable':
        return PaymentReceiveAccountTable(
            id=payment_receive_account.id,
            restaurant_id=payment_receive_account.restaurant_id,
            external_id=payment_receive_account.external_id,
            created_at=tz_to_utc(payment_receive_account.created_at),
            onboarding_completed=payment_receive_account.onboarding_completed,
        )
