from typing import List, Optional

from src.catalogs.domain.model.product import Product
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.product_variant import ProductVariant
from src.catalogs.domain.model.product_variant_validator import ProductVariantValidator
from src.infrastructure.common.config import get_key
from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message
from src.infrastructure.storage.document_type_service import DocumentTypeService
from src.infrastructure.storage.s3_client import S3Client


class ProductVariantService:
    def __init__(self, product_variant_validator: Optional[ProductVariantValidator] = None,
                 product_repository: Optional[ProductRepository] = None,
                 s3_client: Optional[S3Client] = None,
                 document_type_service: Optional[DocumentTypeService] = None):
        self.product_variant_validator = product_variant_validator or ProductVariantValidator()
        self.product_repository = product_repository or ProductRepository()
        self.s3_client = s3_client or S3Client()
        self.document_type_service = document_type_service or DocumentTypeService()

    def add(self, product_variant: ProductVariant, product: Product, image: Optional[bytes]) -> Either[
        List[Message], ProductVariant]:
        messages = self.product_variant_validator.validate_new_product_variant(product_variant, image)
        if messages:
            return Left(messages)

        image_key = self._upload_image(product_variant, image)
        if image_key:
            product.image_key = image_key

        product.variants.append(product_variant)

        self.product_repository.update(product)
        return Right(product)

    def update(self, product_variant: ProductVariant, product: Product, image: Optional[bytes]) -> Either[
        List[Message], ProductVariant]:
        messages = self.product_variant_validator.validate_update_product_variant(product_variant, product, image)
        if messages:
            return Left(messages)

        image_key = self._upload_image(product_variant, image)
        if image_key:
            product.image_key = image_key

        for i, variant in enumerate(product.variants):
            if variant.id == product_variant.id:
                product.variants[i] = product_variant
                break

        self.product_repository.update(product)
        return Right(product)

    def generate_public_image_url(self, product_variant: ProductVariant) -> Optional[str]:
        if not product_variant.image_key:
            return None

        one_hour = 3600
        return self.s3_client.generate_presigned_url(get_key('PRODUCT_VARIANT_IMAGE_BUCKET_NAME'),
                                                     product_variant.image_key, one_hour)

    def _upload_image(self, product_variant: ProductVariant, image: Optional[bytes]) -> Optional[str]:
        if image:
            content_type = self.document_type_service.load_image_type(image)
            image_key = str(product_variant.id)
            self.s3_client.put_binary_object(
                get_key('PRODUCT_VARIANT_IMAGE_BUCKET_NAME'),
                image,
                image_key,
                content_type)
            return image_key
        else:
            return None
