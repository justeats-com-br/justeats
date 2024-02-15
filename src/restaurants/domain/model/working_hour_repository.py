from datetime import time
from typing import List
from uuid import UUID

from sqlalchemy import Column, SmallInteger, Time
from sqlalchemy_utils import UUIDType

from src.infrastructure.common.domain_model import Base
from src.infrastructure.database.connection_factory import Session
from src.restaurants.domain.model.working_hour import WorkingHour


class WorkingHourRepository:
    def __init__(self):
        self.session = Session()

    def add_all(self, working_hours: List[WorkingHour]) -> None:
        self.session.add_all([WorkingHourTable.to_table(working_hour) for working_hour in working_hours])


class WorkingHourTable(Base):
    __tablename__ = 'working_hours'
    id = Column(UUIDType(), primary_key=True)
    restaurant_id = Column(UUIDType(), nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)

    def __init__(self, id: UUID, restaurant_id: UUID, day_of_week: int, opening_time: time, closing_time: time):
        self.id = id
        self.restaurant_id = restaurant_id
        self.day_of_week = day_of_week
        self.opening_time = opening_time
        self.closing_time = closing_time

    def to_domain(self) -> WorkingHour:
        return WorkingHour(
            id=self.id,
            restaurant_id=self.restaurant_id,
            day_of_week=self.day_of_week,
            opening_time=self.opening_time,
            closing_time=self.closing_time
        )

    @staticmethod
    def to_table(working_hour) -> 'WorkingHourTable':
        return WorkingHourTable(
            id=working_hour.id,
            restaurant_id=working_hour.restaurant_id,
            day_of_week=working_hour.day_of_week,
            opening_time=working_hour.opening_time,
            closing_time=working_hour.closing_time
        )
