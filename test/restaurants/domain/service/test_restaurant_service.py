from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.infrastructure.common.config import get_key
from src.infrastructure.common.message import Message, MessageCategory
from src.infrastructure.storage.document_type_service import DocumentTypeService
from src.infrastructure.storage.s3_client import S3Client
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository
from src.restaurants.domain.model.restaurant_validator import RestaurantValidator
from src.restaurants.domain.service.restaurant_service import RestaurantService
from test.restaurants.domain.model.restaurant_factory import RestaurantFactory


class TestRestaurantService:
    @fixture
    def restaurant_validator(self) -> RestaurantValidator:
        return MagicMock()

    @fixture
    def s3_client(self) -> S3Client:
        return MagicMock()

    @fixture
    def restaurant_repository(self) -> RestaurantRepository:
        return MagicMock()

    @fixture
    def document_type_service(self) -> DocumentTypeService:
        return MagicMock()

    @fixture
    def restaurant_service(self, restaurant_validator, s3_client, restaurant_repository,
                           document_type_service) -> RestaurantService:
        return RestaurantService(restaurant_validator, s3_client, restaurant_repository, document_type_service)

    def test_add_with_invalid_restaurant_should_return_validation_messages(self, restaurant_validator,
                                                                           restaurant_service):
        invalid_restaurant = RestaurantFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        restaurant_validator.validate_new_restaurant = MagicMock(return_value=messages)

        add_result = restaurant_service.add(invalid_restaurant, None)

        assert add_result.is_left()
        assert add_result.left() == messages

    def test_add_with_valid_restaurant_and_image_should_return_restaurant(self, restaurant_validator, s3_client,
                                                                          restaurant_repository, document_type_service,
                                                                          restaurant_service):
        restaurant = RestaurantFactory()
        restaurant_validator.validate_new_restaurant = MagicMock(return_value=[])
        s3_client.put_binary_object = MagicMock(return_value='http://bucket.s3.amazonaws.com/key')
        document_type_service.load_image_type = MagicMock(return_value='image/png')
        logo = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82'

        add_result = restaurant_service.add(restaurant, logo)

        assert add_result.is_right()
        assert add_result.right() == restaurant
        assert restaurant.logo_url == 'http://bucket.s3.amazonaws.com/key'
        restaurant_repository.add.assert_called_once_with(restaurant)
        s3_client.put_binary_object.assert_called_once_with(get_key('RESTAURANT_LOGO_BUCKET_NAME'), logo,
                                                            str(restaurant.id),
                                                            'image/png', 'public-read')
