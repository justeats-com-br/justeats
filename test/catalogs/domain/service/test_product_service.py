from gettext import gettext

from mock import MagicMock
from pytest import fixture

from src.catalogs.domain.service.product_service import ProductService
from src.infrastructure.common.config import get_key
from src.infrastructure.common.message import Message, MessageCategory
from test.catalogs.domain.model.product_factory import ProductFactory


class TestProductService:
    @fixture
    def product_validator(self):
        return MagicMock()

    @fixture
    def product_repository(self):
        return MagicMock()

    @fixture
    def s3_client(self):
        return MagicMock()

    @fixture
    def document_type_service(self):
        return MagicMock()

    @fixture
    def product_service(self, product_validator, product_repository, s3_client, document_type_service):
        return ProductService(product_validator, product_repository, s3_client, document_type_service)

    def test_add_with_invalid_product_should_return_validation_messages(self, product_validator, product_service):
        invalid_product = ProductFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        product_validator.validate_new_product = MagicMock(return_value=messages)

        add_result = product_service.add(invalid_product, None)

        assert add_result.is_left()
        assert add_result.left() == messages

    def test_add_with_valid_product_and_image_should_return_product(self, product_validator, s3_client,
                                                                    product_repository, document_type_service,
                                                                    product_service):
        product = ProductFactory()
        product_validator.validate_new_product = MagicMock(return_value=[])
        s3_client.put_binary_object = MagicMock(return_value='http://bucket.s3.amazonaws.com/key')
        document_type_service.load_image_type = MagicMock(return_value='image/png')
        image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82'

        add_result = product_service.add(product, image)

        assert add_result.is_right()
        assert add_result.right() == product
        assert product.image_key == str(product.id)
        product_repository.add.assert_called_once_with(product)
        s3_client.put_binary_object.assert_called_once_with(get_key('PRODUCT_IMAGE_BUCKET_NAME'), image,
                                                            str(product.id),
                                                            'image/png')

    def test_add_with_valid_product_and_no_image_should_return_product(self, product_validator, s3_client,
                                                                       product_repository, document_type_service,
                                                                       product_service):
        product = ProductFactory(image_key=None)
        product_validator.validate_new_product = MagicMock(return_value=[])

        add_result = product_service.add(product, None)

        assert add_result.is_right()
        assert add_result.right() == product
        assert product.image_key is None
        product_repository.add.assert_called_once_with(product)
        s3_client.put_binary_object.assert_not_called()
        document_type_service.load_image_type.assert_not_called()

    def test_update_with_invalid_product_should_return_validation_messages(self, product_validator, product_service):
        invalid_product = ProductFactory()
        messages = [Message(
            category=MessageCategory.VALIDATION,
            target='name',
            message=gettext('Required field'),
            key='empty'
        )]
        product_validator.validate_update_product = MagicMock(return_value=messages)

        update_result = product_service.update(invalid_product, None)

        assert update_result.is_left()
        assert update_result.left() == messages

    def test_update_with_valid_product_and_image_should_return_product(self, product_validator, s3_client,
                                                                       product_repository, document_type_service,
                                                                       product_service):
        product = ProductFactory()
        product_validator.validate_update_product = MagicMock(return_value=[])
        s3_client.put_binary_object = MagicMock(return_value='http://bucket.s3.amazonaws.com/key')
        document_type_service.load_image_type = MagicMock(return_value='image/png')
        image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82'

        update_result = product_service.update(product, image)

        assert update_result.is_right()
        assert update_result.right() == product
        assert product.image_key == str(product.id)
        product_repository.update.assert_called_once_with(product)
        s3_client.put_binary_object.assert_called_once_with(get_key('PRODUCT_IMAGE_BUCKET_NAME'), image,
                                                            str(product.id),
                                                            'image/png')
        document_type_service.load_image_type.assert_called_once_with(image)

    def test_update_with_valid_product_and_no_image_should_return_product(self, product_validator, s3_client,
                                                                          product_repository, document_type_service,
                                                                          product_service):
        product = ProductFactory(image_key=None)
        product_validator.validate_update_product = MagicMock(return_value=[])

        update_result = product_service.update(product, None)

        assert update_result.is_right()
        assert update_result.right() == product
        assert product.image_key is None
        product_repository.update.assert_called_once_with(product)
        s3_client.put_binary_object.assert_not_called()
        document_type_service.load_image_type.assert_not_called()
