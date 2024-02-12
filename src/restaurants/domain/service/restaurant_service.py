from typing import Optional, List

from src.infrastructure.common.config import get_key
from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message
from src.infrastructure.storage.document_type_service import DocumentTypeService
from src.infrastructure.storage.s3_client import S3Client
from src.restaurants.domain.model.restaurant import Restaurant
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository
from src.restaurants.domain.model.restaurant_validator import RestaurantValidator


class RestaurantService:
    def __init__(self, restaurant_validator: Optional[RestaurantValidator] = None,
                 s3_client: Optional[S3Client] = None,
                 restaurant_repository: Optional[RestaurantRepository] = None,
                 document_type_service: Optional[DocumentTypeService] = None):
        self.restaurant_validator = restaurant_validator or RestaurantValidator()
        self.s3_client = s3_client or S3Client()
        self.restaurant_repository = restaurant_repository or RestaurantRepository()
        self.document_type_service = document_type_service or DocumentTypeService()

    def add(self, restaurant: Restaurant, logo: Optional[bytes]) -> Either[List[Message], Restaurant]:
        messages = self.restaurant_validator.validate_new_restaurant(restaurant, logo)
        if messages:
            return Left(messages)

        if logo:
            content_type = self.document_type_service.load_image_type(logo)
            logo_url = self.s3_client.put_binary_object(
                get_key('RESTAURANT_LOGO_BUCKET_NAME'),
                logo,
                str(restaurant.id),
                content_type,
                'public-read')
            restaurant.logo_url = logo_url

        self.restaurant_repository.add(restaurant)
        return Right(restaurant)
