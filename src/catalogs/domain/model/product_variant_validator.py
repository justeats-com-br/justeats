from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.catalogs.domain.model.product import Product
from src.catalogs.domain.model.product_variant import ProductVariant
from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper
from src.infrastructure.storage.document_type_service import DocumentTypeService


class ProductVariantValidations(Validator):
    def __init__(self, document_type_service: DocumentTypeService, product: Optional[Product], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_type_service = document_type_service
        self.product = product

    def _validate_invalid_id(self, constraint, field, value):
        if value and self.product:
            product_variant = [variant for variant in self.product.variants if variant.id == value]
            if not product_variant:
                self._error(field, ErrorDefinition(0, 'invalid_id'))
                self.recent_error.constraint = None

    def _validate_invalid_image_type(self, constraint, field, value):
        if value:
            image_type = self.document_type_service.load_image_type(value)
            if not image_type:
                self._error(field, ErrorDefinition(0, 'invalid_image_type'))
                self.recent_error.constraint = None


validation_schema = {
    'name': {'required': True, 'empty': False, 'maxlength': 100},
    'description': {'required': False, 'nullable': True, 'empty': False, 'maxlength': 300},
    'price': {'required': True, 'empty': False, 'min': 1},
    'image': {'required': False, 'nullable': True, 'invalid_image_type': True},
}


class ProductVariantValidator:
    def __init__(self, document_type_service: Optional[DocumentTypeService] = None):
        self.document_type_service = document_type_service or DocumentTypeService()

    def validate_new_product_variant(self, product_variant: ProductVariant, image: Optional[bytes]) -> List[Message]:
        new_product_variant_validation_schema = {
            **validation_schema,
        }

        validator = ProductVariantValidations(self.document_type_service, None, new_product_variant_validation_schema,
                                              allow_unknown=False)
        validator.validate({
            'name': product_variant.name,
            'description': product_variant.description,
            'price': product_variant.price,
            'image': image,
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_product_variant(self, product_variant: ProductVariant, product: Product,
                                        image: Optional[bytes]) -> List[Message]:
        update_product_variant_validation_schema = {
            **validation_schema,
            'id': {'required': True, 'empty': False, 'invalid_id': True},
        }
        validator = ProductVariantValidations(self.document_type_service, product,
                                              update_product_variant_validation_schema,
                                              allow_unknown=False)
        validator.validate({
            'id': product_variant.id,
            'name': product_variant.name,
            'description': product_variant.description,
            'price': product_variant.price,
            'image': image,
        })
        return MessageMapper.to_messages(validator._errors)
