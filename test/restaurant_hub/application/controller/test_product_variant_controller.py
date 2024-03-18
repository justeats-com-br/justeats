from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.product_factory import ProductTableFactory
from test.catalogs.domain.model.product_variant_factory import ProductVariantFactory
from test.catalogs.domain.model.section_factory import SectionTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestProductVariantController(WebappTest):
    def test_should_add_product_variant_to_product(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        product_variant = ProductVariantFactory()
        page.goto(url_for('main.load_update_product_in_section', section_id=section.id, product_id=product.id,
                          _external=True))
        page.get_by_role("button", name=gettext('Add product variant')).click()
        page.get_by_label(gettext('Name')).fill(product_variant.name)
        page.get_by_label(gettext('Description')).fill(product_variant.description)
        page.get_by_label(gettext('Price')).fill(str(product_variant.price / 100))
        page.get_by_role("button", name=gettext('Add product variant')).click()
        expect(page.get_by_role("link", name=f"{product_variant.name} {product_variant.description}")).to_be_visible()

    def test_should_update_product_variant_in_product(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        product_variant = product.variants[0]
        page.goto(url_for('main.load_update_product_in_section', section_id=section.id, product_id=product.id,
                          _external=True))
        page.get_by_role("link", name=f"{product_variant.name} {product_variant.description}").click()
        new_product_variant_name = 'New product variant name'
        page.get_by_label(gettext('Name')).fill(new_product_variant_name)
        page.get_by_role("button", name=gettext('Update product variant')).click()
        expect(
            page.get_by_role("link", name=f"{new_product_variant_name} {product_variant.description}")).to_be_visible()
