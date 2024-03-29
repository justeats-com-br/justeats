from gettext import gettext

from flask import url_for
from playwright.sync_api import expect

from test.users.domain.model.user_factory import UserFactory
from test.webapp_test import WebappTest


class TestSignUpController(WebappTest):
    def test_should_sign_up(self, page):
        user = UserFactory()
        password = 'SomeStrongPassword@123'
        page.goto(url_for('main.load_sign_up', _external=True))
        page.get_by_label(gettext('Email')).fill(user.email)
        page.get_by_label(gettext('Name')).fill(user.name)
        page.get_by_label(gettext('Password')).fill(password)
        page.get_by_role('button', name=gettext('Sign up')).click()
        expect(page.get_by_role('heading', name=gettext('Restaurant information'), exact=True)).to_be_visible()
