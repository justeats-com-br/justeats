import uuid

from flask import render_template, make_response, url_for

from src.restaurant_hub.application.controller import main, string_form_value, int_form_value, enum_form_value, \
    decimal_form_value
from src.restaurant_hub.infrastructure.auth import auth
from src.restaurants.domain.model.delivery_method import DeliveryMethod, DeliveryType
from src.restaurants.domain.model.delivery_method_repository import DeliveryMethodRepository
from src.restaurants.domain.service.delivery_method_service import DeliveryMethodService


@main.route('/restaurants/<restaurant_id>/delivery-methods', methods=['GET'])
@auth
def list_restaurant_delivery_methods(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    delivery_methods = DeliveryMethodRepository().list_by_restaurant(restaurant_id)
    return render_template('restaurant/delivery_methods/delivery_methods.html', delivery_methods=delivery_methods,
                           restaurant_id=restaurant_id)


@main.route('/restaurants/<restaurant_id>/delivery-method', methods=['GET'])
@auth
def load_add_delivery_method(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    return render_template('restaurant/delivery_methods/delivery_method.html', restaurant_id=restaurant_id)


@main.route('/restaurants/<restaurant_id>/delivery-methods/<delivery_method_id>', methods=['GET'])
@auth
def load_update_delivery_method_in_restaurant(restaurant_id: str, delivery_method_id: str):
    delivery_method_id = uuid.UUID(delivery_method_id)
    delivery_method = DeliveryMethodRepository().load(delivery_method_id)
    return render_template('restaurant/delivery_methods/delivery_method.html',
                           restaurant_id=delivery_method.restaurant_id,
                           **_to_delivery_method_form(delivery_method))


@main.route('/restaurants/<restaurant_id>/delivery-methods', methods=['POST'])
@auth
def add_delivery_method(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    delivery_type = enum_form_value(DeliveryType, 'delivery_type')
    delivery_radius = int_form_value('delivery_radius')
    delivery_fee = int(decimal_form_value('delivery_fee') * 100) if decimal_form_value('delivery_fee') is not None else None
    estimated_delivery_time = int_form_value('estimated_delivery_time')
    delivery_method = DeliveryMethod(
        id=uuid.uuid4(),
        restaurant_id=restaurant_id,
        delivery_type=delivery_type,
        delivery_radius=delivery_radius,
        delivery_fee=delivery_fee,
        estimated_delivery_time=estimated_delivery_time
    )
    result = DeliveryMethodService().add(delivery_method)

    if result.is_left():
        delivery_method.id = None
        return render_template('restaurant/delivery_methods/partials/add_delivery_method_form.html',
                               messages=result.left(),
                               restaurant_id=restaurant_id,
                               **_to_delivery_method_form(delivery_method))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.list_restaurant_delivery_methods', restaurant_id=restaurant_id)
        return response


@main.route('/restaurants/<restaurant_id>/delivery-methods', methods=['PATCH'])
@auth
def update_delivery_method_in_restaurant(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    id = uuid.UUID(string_form_value('id'))
    delivery_method = DeliveryMethodRepository().load(id)
    delivery_type = enum_form_value(DeliveryType, 'delivery_type')
    delivery_radius = int_form_value('delivery_radius')
    delivery_fee = int(decimal_form_value('delivery_fee') * 100) if decimal_form_value('delivery_fee') is not None else None
    estimated_delivery_time = int_form_value('estimated_delivery_time')
    delivery_method.delivery_type = delivery_type
    delivery_method.delivery_radius = delivery_radius
    delivery_method.delivery_fee = delivery_fee
    delivery_method.estimated_delivery_time = estimated_delivery_time

    result = DeliveryMethodService().update(delivery_method)

    if result.is_left():
        return render_template('restaurant/delivery_methods/partials/add_delivery_method_form.html',
                               messages=result.left(),
                               restaurant_id=restaurant_id, **_to_delivery_method_form(delivery_method))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.list_restaurant_delivery_methods', restaurant_id=restaurant_id)
        return response


def _to_delivery_method_form(delivery_method: DeliveryMethod) -> dict[str, any]:
    delivery_method_form = {
        'id': delivery_method.id,
        'delivery_type': delivery_method.delivery_type,
        'delivery_radius': delivery_method.delivery_radius,
        'delivery_fee': delivery_method.delivery_fee,
        'estimated_delivery_time': delivery_method.estimated_delivery_time,
    }

    return {k: v for k, v in delivery_method_form.items() if v is not None}
