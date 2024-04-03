from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.product_factory import ProductTableFactory
from test.catalogs.domain.model.section_factory import SectionTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestCatalogController(WebappTest):
    def test_should_load_catalog(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()

        page.goto(url_for('main.load_catalog', restaurant_id=restaurant.id, _external=True))

        expect(page.get_by_role("link", name=gettext('Add section'))).to_be_visible()
        expect(page.get_by_role("link", name=section.name)).to_be_visible()
        expect(page.get_by_role("link", name=gettext('Add product'))).to_be_visible()
        expect(page.get_by_role("link", name=f"{product.name}")).to_be_visible()
