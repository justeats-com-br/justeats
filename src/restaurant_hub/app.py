from flask import Flask, request
from flask_babel import Babel

from src.infrastructure.common.config import ENVIRONMENT


def get_locale():
    return request.accept_languages.best_match(['en'])


def create_app():
    from src.restaurant_hub.application.controller import main

    app = Flask(__name__)
    babel = Babel(app, locale_selector=get_locale)
    app.secret_key = 'super secret string'
    app.register_blueprint(main)
    return app


if __name__ == "__main__":
    debug = ENVIRONMENT == 'LOCAL'
    create_app().run(debug=debug)
