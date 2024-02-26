import uuid
from collections import defaultdict

from flask import render_template, make_response, url_for, request

from src.catalogs.domain.model.catalog import Catalog
from src.catalogs.domain.model.catalog_repository import CatalogRepository
from src.catalogs.domain.model.product import Status, Product
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.section import Section
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.product_service import ProductService
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

    return render_template('catalog/catalog.html', restaurant_id=restaurant_id, sections=sections,
                           section_products=section_products)


@main.route('/restaurants/<restaurant_id>/section', methods=['GET'])
@auth
def load_add_section(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    return render_template('catalog/section.html', restaurant_id=restaurant_id)


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
                      image_url=None, status=status, variants=[], modifiers=[], created_at=get_utcnow(),
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


def _to_section_form(section: Section) -> dict[str, any]:
    restaurant_form = {
        'name': section.name,
        'description': section.description,
        'sort_order': section.sort_order
    }

    return {k: v for k, v in restaurant_form.items() if v is not None}


def _to_product_form(product: Product) -> dict[str, any]:
    product_form = {
        'id': product.id,
        'section_id': product.section_id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'status': product.status,
        'image_url': product.image_url
    }

    return {k: v for k, v in product_form.items() if v is not None}
