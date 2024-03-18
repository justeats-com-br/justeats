import uuid
from collections import defaultdict

from flask import render_template

from src.catalogs.domain.model.catalog_repository import CatalogRepository
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.product_service import ProductService
from src.restaurant_hub.application.controller import main
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
