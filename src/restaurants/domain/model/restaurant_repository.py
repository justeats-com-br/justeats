from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DECIMAL
from sqlalchemy_utils import UUIDType

from src.infrastructure.common.domain_model import Base
from src.infrastructure.database.connection_factory import Session
from src.restaurants.domain.model.restaurant import Restaurant, Address, Point, State, Category


class RestaurantRepository:
    def __init__(self):
        self.session = Session()

    def add(self, restaurant: Restaurant) -> None:
        self.session.add(RestaurantTable.to_table(restaurant))

    def load_by_document_number(self, document_number: str) -> Optional[Restaurant]:
        result = self.session.query(RestaurantTable).filter(RestaurantTable.document_number == document_number).first()
        return result.to_domain() if result else None


class RestaurantTable(Base):
    __tablename__ = 'restaurants'
    id = Column(UUIDType(), primary_key=True)
    user_id = Column(UUIDType(), nullable=False)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    address_street = Column(String, nullable=False)
    address_number = Column(String, nullable=False)
    address_neighborhood = Column(String, nullable=False)
    address_city = Column(String, nullable=False)
    address_state = Column(String, nullable=False)
    address_zip_code = Column(String, nullable=False)
    address_complement = Column(String, nullable=True)
    address_latitude = Column(DECIMAL, nullable=True)
    address_longitude = Column(DECIMAL, nullable=True)
    document_number = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    description = Column(String, nullable=True)

    def __init__(self, id: UUID, user_id: UUID, category: str, name: str, address_street: str, address_number: str,
                 address_neighborhood: str, address_city: str, address_state: str, address_zip_code: str,
                 address_complement: Optional[str], address_latitude: Optional[str], address_longitude: Optional[str],
                 document_number: str, logo_url: Optional[str], description: Optional[str]):
        self.id = id
        self.user_id = user_id
        self.category = category
        self.name = name
        self.address_street = address_street
        self.address_number = address_number
        self.address_neighborhood = address_neighborhood
        self.address_city = address_city
        self.address_state = address_state
        self.address_zip_code = address_zip_code
        self.address_complement = address_complement
        self.address_latitude = address_latitude
        self.address_longitude = address_longitude
        self.document_number = document_number
        self.logo_url = logo_url
        self.description = description

    def to_domain(self) -> Restaurant:
        return Restaurant(
            id=self.id,
            user_id=self.user_id,
            category=Category[self.category],
            name=self.name,
            address=Address(
                street=self.address_street,
                number=self.address_number,
                neighborhood=self.address_neighborhood,
                city=self.address_city,
                state=State[self.address_state],
                zip_code=self.address_zip_code,
                complement=self.address_complement,
                point=Point(
                    latitude=self.address_latitude,
                    longitude=self.address_longitude
                )
            ),
            document_number=self.document_number,
            logo_url=self.logo_url,
            description=self.description
        )

    @staticmethod
    def to_table(restaurant) -> 'RestaurantTable':
        return RestaurantTable(
            id=restaurant.id,
            user_id=restaurant.user_id,
            category=restaurant.category.value if restaurant.category is not None else None,
            name=restaurant.name,
            address_street=restaurant.address.street if restaurant.address else None,
            address_number=restaurant.address.number if restaurant.address else None,
            address_neighborhood=restaurant.address.neighborhood if restaurant.address else None,
            address_city=restaurant.address.city if restaurant.address else None,
            address_state=restaurant.address.state.value if restaurant.address and restaurant.address.state else None,
            address_zip_code=restaurant.address.zip_code if restaurant.address else None,
            address_complement=restaurant.address.complement if restaurant.address else None,
            address_latitude=restaurant.address.point.latitude if restaurant.address and restaurant.address.point else None,
            address_longitude=restaurant.address.point.longitude if restaurant.address and restaurant.address.point else None,
            document_number=restaurant.document_number,
            logo_url=restaurant.logo_url,
            description=restaurant.description
        )
