from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.modifier_factory import ModifierOptionFactory
from test.catalogs.domain.model.product_factory import ProductTableFactory
from test.catalogs.domain.model.section_factory import SectionTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestModifierOptionController(WebappTest):
    def test_should_add_option_to_modifier(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        modifier = product.modifiers[0]
        option = ModifierOptionFactory()
        page.goto(
            url_for('main.load_add_option_to_modifier', product_id=product.id, modifier_id=modifier.id, _external=True))
        page.get_by_label(gettext('Name')).fill(option.name)
        page.get_by_label(gettext('Description')).fill(option.description)
        page.get_by_label(gettext('Price')).fill(str(option.price / 100))
        page.get_by_role("button", name=gettext('Add option')).click()
        expect(page.get_by_role("link", name=f"{option.name} {option.description}")).to_be_visible()

    def test_should_update_option_to_modifier(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        modifier = product.modifiers[0]
        option = modifier.options[0]
        new_name = 'New option name'
        page.goto(
            url_for('main.load_update_option_in_modifier', product_id=product.id, modifier_id=modifier.id,
                    option_id=option.id, _external=True))
        page.get_by_label(gettext('Name')).fill(new_name)
        page.get_by_role("button", name=gettext('Update option')).click()
        expect(page.get_by_role("link", name=f"{new_name} {option.description}")).to_be_visible()
