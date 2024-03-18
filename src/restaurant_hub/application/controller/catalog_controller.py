import uuid
from collections import defaultdict

from flask import render_template, make_response, url_for, request

from src.catalogs.domain.model.catalog import Catalog
from src.catalogs.domain.model.catalog_repository import CatalogRepository
from src.catalogs.domain.model.modifier import Modifier, ModifierOption
from src.catalogs.domain.model.product import Status, Product
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.product_variant import ProductVariant
from src.catalogs.domain.model.section import Section
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.modifier_option_service import ModifierOptionService
from src.catalogs.domain.service.modifier_service import ModifierService
from src.catalogs.domain.service.product_service import ProductService
from src.catalogs.domain.service.product_variant_service import ProductVariantService
from src.catalogs.domain.service.section_service import SectionService
from src.infrastructure.common.utils import get_utcnow
from src.restaurant_hub.application.controller import main, string_form_value, int_form_value, decimal_form_value, \
    enum_form_value
from src.restaurant_hub.infrastructure.auth import auth


@main.route('/restaurants/<restaurant_id>/catalogs', methods=['GET'])
@auth
def load_catalog(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    catalog = CatalogRepository().load_by_restaurant_id(restaurant_id)
    sections = SectionRepository().list_by_catalog_id(catalog.id) if catalog else []
    section_ids = [section.id for section in sections]
    products = ProductRepository().list_by_section_ids(section_ids)
    section_products = defaultdict(list)
    for product in products:
        section_products[product.section_id].append(product)
    product_service = ProductService()
    product_image_url = {product.id: product_service.generate_public_image_url(product) for product in products if
                         product.image_key}

    return render_template('catalog/catalog.html', restaurant_id=restaurant_id, sections=sections,
                           section_products=section_products, product_image_url=product_image_url)


@main.route('/restaurants/<restaurant_id>/section', methods=['GET'])
@auth
def load_add_section(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    return render_template('catalog/section.html', restaurant_id=restaurant_id)


@main.route('/restaurants/<restaurant_id>/sections/<section_id>', methods=['GET'])
@auth
def load_update_section_in_restaurant(restaurant_id: str, section_id: str):
    section_id = uuid.UUID(section_id)
    section = SectionRepository().load(section_id)
    catalog = CatalogRepository().load(section.catalog_id)
    return render_template('catalog/section.html', restaurant_id=catalog.restaurant_id, **_to_section_form(section))


@main.route('/restaurants/<restaurant_id>/sections', methods=['POST'])
@auth
def add_section(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    name = string_form_value('name')
    description = string_form_value('description')
    sort_order = int_form_value('sort_order')

    catalog_repository = CatalogRepository()
    catalog = catalog_repository.load_by_restaurant_id(restaurant_id)
    if not catalog:
        catalog = Catalog(id=uuid.uuid4(), restaurant_id=restaurant_id, created_at=get_utcnow(),
                          updated_at=get_utcnow())
        catalog_repository.add(catalog)

    section = Section(id=uuid.uuid4(), catalog_id=catalog.id, name=name, description=description, sort_order=sort_order,
                      created_at=get_utcnow(), updated_at=get_utcnow())
    result = SectionService().add(section)

    if result.is_left():
        return render_template('catalog/partials/add_section_form.html', messages=result.left(),
                               restaurant_id=restaurant_id, **_to_section_form(section))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant_id)
        return response


@main.route('/restaurants/<restaurant_id>/sections', methods=['PATCH'])
@auth
def update_section_in_restaurant(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    id = uuid.UUID(string_form_value('id'))
    section = SectionRepository().load(id)
    name = string_form_value('name')
    description = string_form_value('description')
    sort_order = int_form_value('sort_order')
    section.name = name
    section.description = description
    section.sort_order = sort_order

    result = SectionService().update(section)

    if result.is_left():
        return render_template('catalog/partials/add_section_form.html', messages=result.left(),
                               restaurant_id=restaurant_id, **_to_section_form(section))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant_id)
        return response


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
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
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
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
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
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
    image = request.files['image'] if 'image' in request.files else None
    product_variant = ProductVariant(
        id=uuid.uuid4(),
        name=name,
        description=description,
        price=price,
        image_key=None)
    result = ProductVariantService().add(product_variant, product, image.read() if image else None)

    if result.is_left():
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
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
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


@main.route('/products/<product_id>/modifier', methods=['GET'])
@auth
def load_add_modifier_to_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    return render_template('catalog/modifier.html', product=product, section=section)


@main.route('/products/<product_id>/modifiers/<modifier_id>', methods=['GET'])
@auth
def load_update_modifier_in_product(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    modifier_id = uuid.UUID(modifier_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)

    return render_template('catalog/modifier.html', product=product, section=section,
                           **_to_modifier_form(modifier))


@main.route('/products/<product_id>/modifiers', methods=['POST'])
@auth
def add_modifier_to_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    name = string_form_value('name')
    description = string_form_value('description')
    minimum_options = string_form_value('minimum_options')
    maximum_options = string_form_value('maximum_options')
    modifier = Modifier(id=uuid.uuid4(), name=name, description=description, minimum_options=minimum_options,
                        maximum_options=maximum_options, options=[], )

    result = ModifierService().add(product, modifier)

    if result.is_left():
        return render_template('catalog/partials/add_modifier_form.html', messages=result.left(),
                               product=product,
                               **_to_modifier_form(modifier))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=modifier.id)
        return response


@main.route('/products/<product_id>/modifiers', methods=['PATCH'])
@auth
def update_modifier_in_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    id = uuid.UUID(string_form_value('id'))
    product_modifier = next((modifier for modifier in product.modifiers if modifier.id == id), None)
    if not product_modifier:
        response = make_response()
        response.status_code = 404
        return response
    name = string_form_value('name')
    description = string_form_value('description')
    minimum_options = string_form_value('minimum_options')
    maximum_options = string_form_value('maximum_options')
    product_modifier.name = name
    product_modifier.description = description
    product_modifier.minimum_options = minimum_options
    product_modifier.maximum_options = maximum_options
    result = ModifierService().update(product, product_modifier)

    if result.is_left():
        return render_template('catalog/partials/add_modifier_form.html', messages=result.left(),
                               product=product,
                               **_to_modifier_form(product_modifier))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=product_modifier.id)
        return response


@main.route('/products/<product_id>/modifiers/<modifier_id>/option', methods=['GET'])
@auth
def load_add_option_to_modifier(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    modifier_id = uuid.UUID(modifier_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
    return render_template('catalog/option.html', product=product, section=section, modifier=modifier)


@main.route('/products/<product_id>/modifiers/<modifier_id>/options', methods=['POST'])
@auth
def add_option_to_modifier(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    modifier_id = uuid.UUID(modifier_id)
    section = SectionRepository().load(product.section_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)

    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
    option = ModifierOption(
        id=uuid.uuid4(),
        name=name,
        description=description,
        price=price,
    )

    result = ModifierOptionService().add(product, modifier_id, option)

    if result.is_left():
        return render_template('catalog/partials/add_option_form.html', messages=result.left(),
                               product=product, section=section, modifier=modifier,
                               **_to_modifier_option_form(option))
    else:
        _, modifier, _ = result.right()
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=modifier.id)
        return response


@main.route('/products/<product_id>/modifiers/<modifier_id>/options/<option_id>', methods=['GET'])
@auth
def load_update_option_in_modifier(product_id: str, modifier_id: str, option_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    modifier_id = uuid.UUID(modifier_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
    option_id = uuid.UUID(option_id)
    option = next((option for option in modifier.options if option.id == option_id), None)

    return render_template('catalog/option.html', product=product, section=section, modifier=modifier,
                           **_to_modifier_option_form(option))


@main.route('/products/<product_id>/modifiers/<modifier_id>/options', methods=['PATCH'])
@auth
def update_option_in_modifier(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    modifier_id = uuid.UUID(modifier_id)
    section = SectionRepository().load(product.section_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
    id = uuid.UUID(string_form_value('id'))
    option = next((option for option in modifier.options if option.id == id), None)
    if not option:
        response = make_response()
        response.status_code = 404
        return response
    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
    option.name = name
    option.description = description
    option.price = price
    result = ModifierOptionService().update(product, modifier_id, option)

    if result.is_left():
        return render_template('catalog/partials/add_option_form.html', messages=result.left(),
                               product=product, section=section, modifier=modifier,
                               **_to_modifier_option_form(option))
    else:
        _, modifier, _ = result.right()
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=modifier.id)
        return response


def _to_section_form(section: Section) -> dict[str, any]:
    restaurant_form = {
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'sort_order': section.sort_order
    }

    return {k: v for k, v in restaurant_form.items() if v is not None}


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


def _to_modifier_form(modifier: Modifier) -> dict[str, any]:
    modifier_form = {
        'id': modifier.id,
        'name': modifier.name,
        'description': modifier.description,
        'minimum_options': modifier.minimum_options,
        'maximum_options': modifier.maximum_options,
        'options': modifier.options,
    }

    return {k: v for k, v in modifier_form.items() if v is not None}


def _to_modifier_option_form(option: ModifierOption) -> dict[str, any]:
    modifier_form = {
        'id': option.id,
        'name': option.name,
        'description': option.description,
        'price': option.price,
    }

    return {k: v for k, v in modifier_form.items() if v is not None}
