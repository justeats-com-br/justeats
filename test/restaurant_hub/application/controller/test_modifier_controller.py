from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.modifier_factory import ModifierFactory
from test.catalogs.domain.model.product_factory import ProductTableFactory
from test.catalogs.domain.model.section_factory import SectionTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestModifierController(WebappTest):
    def test_should_add_modifier_to_product(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        modifier = ModifierFactory()
        page.goto(url_for('main.load_add_modifier_to_product', product_id=product.id, _external=True))
        page.get_by_label(gettext('Name')).fill(modifier.name)
        page.get_by_label(gettext('Description')).fill(modifier.description)
        page.get_by_label(gettext('Minimum options')).fill(str(modifier.minimum_options))
        page.get_by_label(gettext('Maximum options')).fill(str(modifier.maximum_options))
        page.get_by_role("button", name=gettext('Add modifier')).click()
        expect(page.get_by_role("button", name=gettext('Add option'))).to_be_visible()

    def test_should_update_modifier_in_product(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        modifier = product.modifiers[0]
        new_name = 'Modifier new name'
        page.goto(url_for('main.load_update_modifier_in_product', product_id=product.id,
                          modifier_id=modifier.id, _external=True))
        page.get_by_label(gettext('Name')).fill(new_name)
        page.get_by_role("button", name=gettext('Update modifier')).click()
        expect(page.get_by_role("button", name=gettext('Add option'))).to_be_visible()
