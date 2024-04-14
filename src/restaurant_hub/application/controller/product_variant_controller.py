import uuid

from flask import render_template, make_response, url_for, request

from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.product_variant import ProductVariant
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.product_variant_service import ProductVariantService
from src.restaurant_hub.application.controller import main, string_form_value, decimal_form_value
from src.restaurant_hub.infrastructure.auth import auth


@main.route('/products/<product_id>/product-variant', methods=['GET'])
@auth
def load_add_product_variant_to_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    return render_template('catalog/product_variant.html', product=product, section=section)


@main.route('/products/<product_id>/product-variants/<product_variant_id>', methods=['GET'])
@auth
def load_update_product_variant_in_product(product_id: str, product_variant_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    product_variant_id = uuid.UUID(product_variant_id)
    product_variant = next((variant for variant in product.variants if variant.id == product_variant_id), None)

    return render_template('catalog/product_variant.html', product=product, section=section,
                           **_to_product_variant_form(product_variant))


@main.route('/products/<product_id>/product-variants', methods=['POST'])
@auth
def add_product_variant(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') is not None else None
    image = request.files['image'] if 'image' in request.files else None
    product_variant = ProductVariant(
        id=uuid.uuid4(),
        name=name,
        description=description,
        price=price,
        image_key=None)
    result = ProductVariantService().add(product_variant, product, image.read() if image else None)

    if result.is_left():
        product_variant.id = None
        return render_template('catalog/partials/add_product_variant_form.html', messages=result.left(),
                               product=product,
                               **_to_product_variant_form(product_variant))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_product_in_section', section_id=product.section_id,
                                                  product_id=product.id)
        return response


@main.route('/products/<product_id>/product-variants', methods=['PATCH'])
@auth
def update_product_variant(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    id = uuid.UUID(string_form_value('id'))
    product_variant = next((variant for variant in product.variants if variant.id == id), None)
    if not product_variant:
        response = make_response()
        response.status_code = 404
        return response
    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') is not None else None
    image = request.files['image'] if 'image' in request.files else None
    product_variant.name = name
    product_variant.description = description
    product_variant.price = price
    result = ProductVariantService().update(product_variant, product, image.read() if image else None)

    if result.is_left():
        return render_template('catalog/partials/add_product_variant_form.html', messages=result.left(),
                               product=product,
                               **_to_product_variant_form(product_variant))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_product_in_section', section_id=product.section_id,
                                                  product_id=product.id)
        return response


def _to_product_variant_form(product_variant: ProductVariant) -> dict[str, any]:
    product_variant_form = {
        'id': product_variant.id,
        'name': product_variant.name,
        'description': product_variant.description,
        'price': product_variant.price,
        'image_key': product_variant.image_key,
        'image_url': ProductVariantService().generate_public_image_url(product_variant)
    }

    return {k: v for k, v in product_variant_form.items() if v is not None}
