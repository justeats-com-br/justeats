import re
import uuid

from flask import render_template, make_response, url_for
from flask import request

from src.restaurant_hub.application.controller import main, string_form_value, enum_form_value, decimal_form_value
from src.restaurant_hub.infrastructure.auth import auth, current_user
from src.restaurants.domain.model.restaurant import Category, State, Restaurant, Address, Point
from src.restaurants.domain.service.restaurant_service import RestaurantService


@main.route('/restaurants', methods=['GET'])
def load_add_restaurant():
    return render_template('restaurant/add_restaurant.html')


@main.route('/restaurants', methods=['POST'])
@auth
def add_restaurant():
    user = current_user()
    name = string_form_value('name')
    category = enum_form_value(Category, 'category')
    document_number = re.sub('[^0-9]', '', string_form_value('document_number')) if string_form_value(
        'document_number') else None
    description = string_form_value('description')
    logo = request.files['logo'] if 'logo' in request.files else None
    address = string_form_value('address')
    place_id = string_form_value('place_id')
    zip_code = re.sub('[^0-9]', '', string_form_value('zip_code')) if string_form_value('zip_code') else None
    state = enum_form_value(State, 'state')
    city = string_form_value('city')
    neighborhood = string_form_value('neighborhood')
    street = string_form_value('street')
    street_number = string_form_value('street_number')
    address_complement = string_form_value('address_complement')
    latitude = decimal_form_value('latitude')
    longitude = decimal_form_value('longitud')
    point = Point(latitude=latitude, longitude=longitude) if latitude and longitude else None
    restaurant = Restaurant(id=uuid.uuid4(), user_id=user.id, category=category, name=name,
                            address=Address(street=street, number=street_number, neighborhood=neighborhood, city=city,
                                            state=state, zip_code=zip_code, complement=address_complement,
                                            point=point),
                            document_number=document_number, logo_key=None, description=description)

    result = RestaurantService().add(restaurant, logo.read() if logo else None)

    if result.is_left():
        return render_template('restaurant/partials/add_restaurant_form.html', messages=result.left(),
                               address=address, place_id=place_id, **_to_restaurant_form(restaurant))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_add_working_hours', restaurant_id=restaurant.id)
        return response


def _to_restaurant_form(restaurant: Restaurant) -> dict[str, any]:
    restaurant_form = {
        'name': restaurant.name,
        'category': restaurant.category,
        'document_number': restaurant.document_number,
        'description': restaurant.description,
        'zip_code': restaurant.address.zip_code,
        'state': restaurant.address.state,
        'city': restaurant.address.city,
        'neighborhood': restaurant.address.neighborhood,
        'street': restaurant.address.street,
        'street_number': restaurant.address.number,
        'address_complement': restaurant.address.complement,
    }

    return {k: v for k, v in restaurant_form.items() if v is not None}
