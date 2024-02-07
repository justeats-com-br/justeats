from typing import Optional
from uuid import UUID

from src.infrastructure.common.config import get_key
from src.infrastructure.common.domain_event import EventType, DomainEvent
from src.infrastructure.common.domain_model import DomainModel
from src.infrastructure.topic.sns_client import SnsClient


class DomainEventNotifier:
    def __init__(self, sns_client: Optional[SnsClient] = None):
        self.sns_client = sns_client or SnsClient()

    def notify_event(self, id: UUID, domain: DomainModel, event_type: EventType) -> None:
        event = DomainEvent(id=id, type=event_type, domain=domain)
        self.sns_client.send_message(get_key("DOMAIN_EVENTS_TOPIC"), event)
