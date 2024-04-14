from enum import Enum
from gettext import gettext
from typing import Optional
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class DeliveryType(Enum):
    PICKUP = 'PICKUP'
    DELIVERY = 'DELIVERY'

    def user_friendly_name(self):
        return {
            self.PICKUP: gettext('Pickup'),
            self.DELIVERY: gettext('Delivery')
        }[self]


class DeliveryMethod(DomainModel):
    def __init__(self, id: UUID, restaurant_id: UUID, delivery_type: DeliveryType, delivery_radius: Optional[int],
                 delivery_fee: int,
                 estimated_delivery_time: int):
        self.id = id
        self.restaurant_id = restaurant_id
        self.delivery_type = delivery_type
        self.delivery_radius = delivery_radius
        self.delivery_fee = delivery_fee
        self.estimated_delivery_time = estimated_delivery_time
