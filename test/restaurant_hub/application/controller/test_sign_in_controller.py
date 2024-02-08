from flask import url_for
from playwright.sync_api import expect

from test.webapp_test import WebappTest


class TestSignInController(WebappTest):
    def test_should_sign_in(self, cognito_user, logged_user_password, page):
        email, _, _ = cognito_user
        page.goto(url_for('main.load_sign_in', _external=True))
        page.get_by_label("Email").click()
        page.get_by_label("Email").fill(email)
        page.get_by_label("Password").click()
        page.get_by_label("Password").fill(logged_user_password)
        page.get_by_role("button", name="Sign in").click()
        expect(page.get_by_role("heading", name="Restaurant Hub", exact=True)).to_be_visible()
