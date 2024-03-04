from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestWorkingHourController(WebappTest):
    def test_should_add_working_hours(self, logged_user, page):
        restaurant_record = RestaurantTableFactory.create(user_id=logged_user.id)
        page.goto(url_for('main.load_add_working_hours', restaurant_id=restaurant_record.id, _external=True))
        page.get_by_label('Day of Week').select_option('1')
        page.get_by_label('Opening Time').fill('08:00')
        page.get_by_label('Closing Time').fill('22:00')
        page.get_by_role('button', name=gettext('Add More Hours')).click()
        page.locator('#day_of_week').nth(1).select_option('2')
        page.locator("#opening_time").nth(1).fill('12:00')
        page.locator('#closing_time').nth(1).fill('20:00')
        page.get_by_role('button', name=gettext('Save Working Hours')).click()

        expect(page.get_by_role('heading', name=gettext('Catalog'), exact=True)).to_be_visible()
