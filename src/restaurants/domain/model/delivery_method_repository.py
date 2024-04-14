from typing import Optional, List
from uuid import UUID

from sqlalchemy import Column, String, Integer
from sqlalchemy_utils import UUIDType

from src.infrastructure.common.domain_model import Base
from src.infrastructure.database.connection_factory import Session
from src.restaurants.domain.model.delivery_method import DeliveryMethod, DeliveryType


class DeliveryMethodRepository:
    def __init__(self):
        self.session = Session()

    def load(self, id: UUID) -> Optional[DeliveryMethod]:
        result = self.session.query(DeliveryMethodTable).get(id)
        return result.to_domain() if result else None

    def list_by_restaurant(self, restaurant_id: UUID) -> List[DeliveryMethod]:
        results = self.session.query(DeliveryMethodTable).filter_by(restaurant_id=restaurant_id).all()
        return [result.to_domain() for result in results]

    def add(self, delivery_method: DeliveryMethod) -> None:
        self.session.add(DeliveryMethodTable.to_table(delivery_method))

    def update(self, delivery_method: DeliveryMethod) -> None:
        self.session.merge(DeliveryMethodTable.to_table(delivery_method))

    def load_by_restaurant_and_delivery_type(self, restaurant_id: UUID, delivery_type: DeliveryType) -> Optional[
        DeliveryMethod]:
        result = self.session.query(DeliveryMethodTable).filter_by(restaurant_id=restaurant_id,
                                                                   delivery_type=delivery_type.value).first()
        return result.to_domain() if result else None


class DeliveryMethodTable(Base):
    __tablename__ = 'delivery_methods'
    id = Column(UUIDType(), primary_key=True)
    restaurant_id = Column(UUIDType(), nullable=False)
    delivery_type = Column(String, nullable=False)
    delivery_radius = Column(Integer, nullable=True)
    delivery_fee = Column(Integer, nullable=False)
    estimated_delivery_time = Column(Integer, nullable=False)

    def __init__(self, id: UUID, restaurant_id: UUID, delivery_type: str, delivery_radius: int, delivery_fee: int,
                 estimated_delivery_time: int):
        self.id = id
        self.restaurant_id = restaurant_id
        self.delivery_type = delivery_type
        self.delivery_radius = delivery_radius
        self.delivery_fee = delivery_fee
        self.estimated_delivery_time = estimated_delivery_time

    def to_domain(self) -> DeliveryMethod:
        return DeliveryMethod(
            id=self.id,
            restaurant_id=self.restaurant_id,
            delivery_type=DeliveryType(self.delivery_type),
            delivery_radius=self.delivery_radius,
            delivery_fee=self.delivery_fee,
            estimated_delivery_time=self.estimated_delivery_time
        )

    @staticmethod
    def to_table(working_hour) -> 'DeliveryMethodTable':
        return DeliveryMethodTable(
            id=working_hour.id,
            restaurant_id=working_hour.restaurant_id,
            delivery_type=working_hour.delivery_type.value,
            delivery_radius=working_hour.delivery_radius,
            delivery_fee=working_hour.delivery_fee,
            estimated_delivery_time=working_hour.estimated_delivery_time
        )
