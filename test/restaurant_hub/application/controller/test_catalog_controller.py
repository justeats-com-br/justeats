from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.product_factory import ProductFactory, ProductTableFactory
from test.catalogs.domain.model.section_factory import SectionFactory, SectionTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestCatalogController(WebappTest):
    def test_should_add_section(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        section = SectionFactory()
        page.goto(url_for('main.load_catalog', restaurant_id=restaurant.id, _external=True))
        page.get_by_role("link", name=gettext('Add section')).click()
        page.get_by_label(gettext('Name')).fill(section.name)
        page.get_by_label(gettext('Description')).fill(section.description)
        page.get_by_label(gettext('Sort order')).fill(str(section.sort_order))
        page.get_by_role("button", name=gettext('Add section')).click()
        expect(page.get_by_role('heading', name=section.name)).to_be_visible()

    def test_should_add_product_to_section(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductFactory()
        page.goto(url_for('main.load_catalog', restaurant_id=restaurant.id, _external=True))
        page.get_by_role("link", name=gettext('Add product')).click()
        page.get_by_label(gettext('Name')).fill(product.name)
        page.get_by_label(gettext('Description')).fill(product.description)
        page.get_by_label(gettext('Price')).fill(str(product.price / 100))
        page.get_by_label(gettext('Status')).select_option(product.status.value)
        page.get_by_role("button", name=gettext('Add product')).click()
        expect(page.get_by_role("link", name=f"{product.name} {product.description}")).to_be_visible()

    def test_should_update_product_in_section(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        page.goto(url_for('main.load_catalog', restaurant_id=restaurant.id, _external=True))
        page.get_by_role("link", name=f"{product.name} {product.description}").click()
        expect(page.get_by_label(gettext('Name'))).to_have_value(product.name)
        expect(page.get_by_label(gettext('Description'))).to_have_value(product.description)
        expect(page.get_by_label(gettext('Price'))).to_have_value(str(product.price / 100))
        expect(page.get_by_label(gettext('Status'))).to_have_value(product.status.value)
        new_product_name = 'New product name'
        page.get_by_label(gettext('Name')).fill(new_product_name)
        page.get_by_role("button", name=gettext('Update product')).click()
        expect(page.get_by_role("link", name=f"{new_product_name} {product.description}")).to_be_visible()
