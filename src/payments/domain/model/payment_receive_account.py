from datetime import datetime
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class PaymentReceiveAccount(DomainModel):
    def __init__(self, id: UUID, restaurant_id: UUID, external_id: str, created_at: datetime,
                 onboarding_completed: bool = False):
        self.id = id
        self.restaurant_id = restaurant_id
        self.external_id = external_id
        self.created_at = created_at
        self.onboarding_completed = onboarding_completed
