import re
import uuid
from decimal import Decimal

from flask import render_template, make_response, url_for
from flask import request

from src.restaurant_hub.application.controller import main
from src.restaurant_hub.infrastructure.auth import auth, current_user
from src.restaurants.domain.model.restaurant import Category, State, Restaurant, Address, Point
from src.restaurants.domain.service.restaurant_service import RestaurantService


@main.route('/restaurants', methods=['GET'])
def load_add_restaurant():
    available_categories = [category for category in Category]
    return render_template('restaurant/add_restaurant.html',
                           available_categories=available_categories)


@main.route('/restaurants', methods=['POST'])
@auth
def add_restaurant():
    user = current_user()
    name = request.form['name']
    category = Category[request.form['category']] if request.form['category'] else None
    document_number = re.sub('[^0-9]', '', request.form['document_number']) if request.form['document_number'] else None
    description = request.form['description']
    logo = request.files['logo'] if 'logo' in request.files else None
    address = request.form['address']
    place_id = request.form['place_id']
    zip_code = re.sub('[^0-9]', '', request.form['zip_code']) if request.form['zip_code'] else None
    state = State[request.form['state']] if request.form['state'] else None
    city = request.form['city']
    neighborhood = request.form['neighborhood']
    street = request.form['street']
    street_number = request.form['street_number']
    address_complement = request.form['address_complement']
    latitude = Decimal(request.form['latitude']) if request.form['latitude'] else None
    longitude = Decimal(request.form['longitude']) if request.form['longitude'] else None
    point = Point(latitude=latitude, longitude=longitude) if latitude and longitude else None
    restaurant = Restaurant(id=uuid.uuid4(), user_id=user.id, category=category, name=name,
                            address=Address(street=street, number=street_number, neighborhood=neighborhood, city=city,
                                            state=state, zip_code=zip_code, complement=address_complement,
                                            point=point),
                            document_number=document_number, logo_url=None, description=description)

    result = RestaurantService().add(restaurant, logo.read() if logo else None)

    if result.is_left():
        available_categories = [category for category in Category]
        return render_template('restaurant/partials/add_restaurant_form.html', messages=result.left(),
                               address=address, place_id=place_id, available_categories=available_categories,
                               **_to_restaurant_form(restaurant))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_add_working_hours', restaurant_id=restaurant.id)
        return response


@main.route('/restaurants/<restaurant_id>/working-hours', methods=['GET'])
def load_add_working_hours(restaurant_id: str):
    return render_template('restaurant/add_working_hours.html')


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
