from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.restaurants.domain.model.delivery_method_factory import DeliveryMethodFactory, DeliveryMethodTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.webapp_test import WebappTest


class TestProductController(WebappTest):
    def test_should_add_delivery_method_to_restaurant(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        delivery_method = DeliveryMethodFactory()
        page.goto(url_for('main.list_restaurant_delivery_methods', restaurant_id=restaurant.id, _external=True))
        page.get_by_role("link", name=gettext('Add delivery method')).click()
        page.get_by_label(gettext('Delivery type')).select_option(delivery_method.delivery_type.value)
        page.get_by_label(gettext('Delivery radius')).fill(str(delivery_method.delivery_radius))
        page.get_by_label(gettext('Delivery fee')).fill(str(delivery_method.delivery_fee / 100))
        page.get_by_label(gettext('Estimated delivery time')).fill(str(delivery_method.estimated_delivery_time))
        page.get_by_role("button", name=gettext('Add delivery method')).click()
        expect(page.get_by_role("link",
                                name=f"{delivery_method.delivery_radius} {gettext('Km')} - {delivery_method.estimated_delivery_time} {gettext('Minutes')}")).to_be_visible()

    def test_should_update_delivery_method_to_restaurant(self, logged_user, page):
        restaurant = RestaurantTableFactory.create(user_id=logged_user.id).to_domain()
        delivery_method = DeliveryMethodTableFactory.create(restaurant_id=restaurant.id).to_domain()
        page.goto(url_for('main.list_restaurant_delivery_methods', restaurant_id=restaurant.id, _external=True))
        page.get_by_role("link",
                         name=f"{delivery_method.delivery_radius} {gettext('Km')} - {delivery_method.estimated_delivery_time} {gettext('Minutes')}").click()
        new_delivery_radius = 9999
        page.get_by_label(gettext('Delivery radius')).fill(str(new_delivery_radius))
        page.get_by_role("button", name=gettext('Update delivery method')).click()
        expect(page.get_by_role("link",
                                name=f"{new_delivery_radius} {gettext('Km')} - {delivery_method.estimated_delivery_time} {gettext('Minutes')}")).to_be_visible()
