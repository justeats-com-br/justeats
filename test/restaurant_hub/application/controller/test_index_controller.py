from flask import url_for
from playwright.sync_api import expect

from test.webapp_test import WebappTest


class TestIndexController(WebappTest):
    def test_should_load_index(self, page):
        page.goto(url_for('main.load_index', _external=True))
        expect(page.get_by_role("heading", name="Restaurant Hub", exact=True)).to_be_visible()
