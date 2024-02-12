from datetime import time
from uuid import UUID

from src.infrastructure.common.domain_model import DomainModel


class WorkingHour(DomainModel):
    def __init__(self, id: UUID, restaurant_id: UUID, day_of_week: int, opening_time: time, closing_time: time):
        self.id = id
        self.restaurant_id = restaurant_id
        self.day_of_week = day_of_week
        self.opening_time = opening_time
        self.closing_time = closing_time
