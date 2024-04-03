from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.section_factory import SectionFactory, SectionTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestSectionController(WebappTest):
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

    def test_should_update_section(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        new_name = 'New section name'
        page.goto(url_for('main.load_update_section_in_restaurant', restaurant_id=restaurant.id, section_id=section.id,
                          _external=True))
        page.get_by_label(gettext('Name')).fill(new_name)
        page.get_by_label(gettext('Description')).fill(section.description)
        page.get_by_label(gettext('Sort order')).fill(str(section.sort_order))
        page.get_by_role("button", name=gettext('Update section')).click()
        expect(page.get_by_role('heading', name=new_name)).to_be_visible()
