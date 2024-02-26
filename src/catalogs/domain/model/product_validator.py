from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.catalogs.domain.model.product import Product, Status
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.section_repository import SectionRepository
from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper
from src.infrastructure.storage.document_type_service import DocumentTypeService


class ProductValidations(Validator):
    def __init__(self, section_repository: SectionRepository, document_type_service: DocumentTypeService,
                 product_repository: ProductRepository, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section_repository = section_repository
        self.document_type_service = document_type_service
        self.product_repository = product_repository

    def _validate_invalid_id(self, constraint, field, value):
        if value:
            product = self.product_repository.load(value)
            if not product:
                self._error(field, ErrorDefinition(0, 'invalid_id'))
                self.recent_error.constraint = None

    def _validate_invalid_section_id(self, constraint, field, value):
        if value:
            section = self.section_repository.load(value)
            if not section:
                self._error(field, ErrorDefinition(0, 'invalid_section_id'))
                self.recent_error.constraint = None

    def _validate_invalid_image_type(self, constraint, field, value):
        if value:
            image_type = self.document_type_service.load_image_type(value)
            if not image_type:
                self._error(field, ErrorDefinition(0, 'invalid_image_type'))
                self.recent_error.constraint = None


validation_schema = {
    'section_id': {'required': True, 'empty': False, 'invalid_section_id': True},
    'name': {'required': True, 'empty': False, 'maxlength': 100},
    'description': {'required': False, 'nullable': True, 'empty': False, 'maxlength': 300},
    'price': {'required': True, 'empty': False, 'min': 1},
    'status': {'required': True, 'empty': False, 'allowed': [status for status in Status]},
    'image': {'required': False, 'nullable': True, 'invalid_image_type': True},
}


class ProductValidator:
    def __init__(self, section_repository: Optional[SectionRepository] = None,
                 document_type_service: Optional[DocumentTypeService] = None,
                 product_repository: Optional[ProductRepository] = None):
        self.section_repository = section_repository or SectionRepository()
        self.document_type_service = document_type_service or DocumentTypeService()
        self.product_repository = product_repository or ProductRepository()

    def validate_new_product(self, product: Product, image: Optional[bytes]) -> List[Message]:
        new_product_validation_schema = {
            **validation_schema,
        }

        validator = ProductValidations(self.section_repository, self.document_type_service, self.product_repository,
                                       new_product_validation_schema,
                                       allow_unknown=False)
        validator.validate({
            'section_id': product.section_id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'status': product.status,
            'image': image,
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_product(self, product: Product, image: Optional[bytes]) -> List[Message]:
        update_product_validation_schema = {
            **validation_schema,
            'id': {'required': True, 'empty': False, 'invalid_id': True},
        }
        validator = ProductValidations(self.section_repository, self.document_type_service, self.product_repository,
                                       update_product_validation_schema,
                                       allow_unknown=False)
        validator.validate({
            'id': product.id,
            'section_id': product.section_id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'status': product.status,
            'image': image,
        })
        return MessageMapper.to_messages(validator._errors)
