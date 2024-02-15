import tempfile
from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.restaurants.domain.model.restaurant_factory import RestaurantFactory, RestaurantTableFactory
from test.webapp_test import WebappTest


class TestRestaurantController(WebappTest):
    def test_should_add_restaurant(self, logged_user, page):
        logo = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82'
        with tempfile.NamedTemporaryFile(delete=False) as logo_tmp_file:
            logo_file_name = logo_tmp_file.name
            logo_tmp_file.write(logo)
            logo_tmp_file.flush()

            page.goto(url_for('main.load_add_restaurant', _external=True))

            restaurant = RestaurantFactory()
            page.get_by_label(gettext('Name')).fill(restaurant.name)
            page.get_by_label(gettext('Category')).select_option(restaurant.category.value)
            page.get_by_label(gettext('Document number')).fill(restaurant.document_number)
            page.locator('#description').fill(restaurant.description)
            page.get_by_label(gettext('Logo')).set_input_files(logo_file_name)
            full_address = f'{restaurant.address.street}, {restaurant.address.number}, {restaurant.address.neighborhood}, ' \
                           f'{restaurant.address.city}, {restaurant.address.state.value}, {restaurant.address.zip_code}'
            page.get_by_label(gettext('Address'), exact=True).fill(full_address)
            page.get_by_label(gettext('Address complement')).fill(restaurant.address.complement)
            page.get_by_role('button', name=gettext('Add restaurant')).click()

            expect(page.get_by_role('heading', name='Working hours', exact=True)).to_be_visible()

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

        expect(page.get_by_role('heading', name='Restaurant Hub', exact=True)).to_be_visible()
