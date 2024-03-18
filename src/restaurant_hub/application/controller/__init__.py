from decimal import Decimal

from babel import Locale
from babel.numbers import get_currency_symbol, get_territory_currencies
from flask import Blueprint, request
from flask_babel import format_currency

from src.catalogs.domain.model.product import Status
from src.infrastructure.common.config import ENVIRONMENT, get_key
from src.infrastructure.database.connection_factory import Session
from src.restaurant_hub.app import get_locale
from src.restaurants.domain.model.restaurant import Category

main = Blueprint('main', __name__)

int_form_value = lambda field_name: int(request.form[field_name]) if field_name in request.form and request.form[
    field_name] else None

decimal_form_value = lambda field_name: Decimal(request.form[field_name]) if field_name in request.form and \
                                                                             request.form[field_name] else None

string_form_value = lambda field_name: request.form[field_name] if field_name in request.form and request.form[
    field_name] else None

enum_form_value = lambda enum, field_name: enum[request.form[field_name]] if field_name in request.form and \
                                                                             request.form[field_name] else None

decimal_form_value = lambda field_name: Decimal(request.form[field_name]) if field_name in request.form and \
                                                                             request.form[field_name] else None


@main.teardown_request
def closeDatabaseSession(e):
    if ENVIRONMENT != 'TEST':
        if e is not None:
            Session().rollback()
        else:
            Session().commit()


def get_currency_code():
    try:
        return get_currency_symbol(get_territory_currencies(Locale.parse(get_locale()).territory)[0])
    except Exception as e:
        return '$'


@main.context_processor
def inject_environment_variables():
    return dict(
        ENVIRONMENT=ENVIRONMENT,
        PLACES_API_KEY=get_key('PLACES_API_KEY'),
        format_currency=format_currency,
        currency_code=get_currency_code(),
        available_restaurant_categories=[category for category in Category],
        available_product_statuses=[status for status in Status],
    )


from . import index_controller
from . import sign_up_controller
from . import sign_in_controller
from . import recovery_password_controller
from . import restaurant_controller
from . import working_hour_controller
from . import catalog_controller
from . import modifier_controller
from . import modifier_option_controller
from . import product_controller
from . import product_variant_controller
from . import section_controller
