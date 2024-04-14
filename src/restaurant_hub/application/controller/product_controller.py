import uuid

from flask import render_template, make_response, url_for, request

from src.catalogs.domain.model.catalog_repository import CatalogRepository
from src.catalogs.domain.model.product import Status, Product
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.product_service import ProductService
from src.catalogs.domain.service.product_variant_service import ProductVariantService
from src.infrastructure.common.utils import get_utcnow
from src.restaurant_hub.application.controller import main, string_form_value, decimal_form_value, \
    enum_form_value
from src.restaurant_hub.infrastructure.auth import auth


@main.route('/sections/<section_id>/product', methods=['GET'])
@auth
def load_add_product_to_section(section_id: str):
    section_id = uuid.UUID(section_id)
    section = SectionRepository().load(section_id)
    catalog = CatalogRepository().load(section.catalog_id)
    return render_template('catalog/product.html', section=section, restaurant_id=catalog.restaurant_id)


@main.route('/sections/<section_id>/products/<product_id>', methods=['GET'])
@auth
def load_update_product_in_section(section_id: str, product_id: str):
    section_id = uuid.UUID(section_id)
    section = SectionRepository().load(section_id)
    catalog = CatalogRepository().load(section.catalog_id)
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    return render_template('catalog/product.html', section=section, restaurant_id=catalog.restaurant_id,
                           **_to_product_form(product))


@main.route('/sections/<section_id>/products', methods=['POST'])
@auth
def add_product(section_id: str):
    section_id = uuid.UUID(section_id)
    section = SectionRepository().load(section_id)
    restaurant_id = CatalogRepository().load(section.catalog_id).restaurant_id
    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') is not None else None
    image = request.files['image'] if 'image' in request.files else None
    status = enum_form_value(Status, 'status')
    product = Product(id=uuid.uuid4(), section_id=section_id, name=name, description=description, price=price,
                      image_key=None, status=status, variants=[], modifiers=[], created_at=get_utcnow(),
                      updated_at=get_utcnow())
    result = ProductService().add(product, image.read() if image else None)

    if result.is_left():
        return render_template('catalog/partials/add_product_form.html', messages=result.left(), section=section,
                               **_to_product_form(product))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant_id)
        return response


@main.route('/sections/<section_id>/products', methods=['PATCH'])
@auth
def update_product(section_id: str):
    section_id = uuid.UUID(section_id)
    section = SectionRepository().load(section_id)
    restaurant_id = CatalogRepository().load(section.catalog_id).restaurant_id
    id = uuid.UUID(string_form_value('id'))
    product = ProductRepository().load(id)
    if not product or product.section_id != section_id:
        response = make_response()
        response.status_code = 404
        return response

    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') is not None else None
    image = request.files['image'] if 'image' in request.files else None
    status = enum_form_value(Status, 'status')
    product.name = name
    product.description = description
    product.price = price
    product.status = status
    result = ProductService().update(product, image.read() if image else None)

    if result.is_left():
        return render_template('catalog/partials/add_product_form.html', messages=result.left(), section=section,
                               **_to_product_form(product))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant_id)
        return response


def _to_product_form(product: Product) -> dict[str, any]:
    product_variant_service = ProductVariantService()
    product_variant_image_url = {product_variant.id: product_variant_service.generate_public_image_url(product_variant)
                                 for product_variant in product.variants if product_variant.image_key}

    product_form = {
        'id': product.id,
        'section_id': product.section_id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'status': product.status,
        'image_key': product.image_key,
        'variants': product.variants,
        'modifiers': product.modifiers,
        'image_url': ProductService().generate_public_image_url(product),
        'product_variant_image_url': product_variant_image_url,
    }

    return {k: v for k, v in product_form.items() if v is not None}
