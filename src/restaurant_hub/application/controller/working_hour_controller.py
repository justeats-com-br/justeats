import uuid
from datetime import datetime
from uuid import UUID

from flask import render_template, make_response, url_for
from flask import request

from src.restaurant_hub.application.controller import main
from src.restaurant_hub.infrastructure.auth import auth
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository
from src.restaurants.domain.model.working_hour import WorkingHour
from src.restaurants.domain.model.working_hour_repository import WorkingHourRepository


@main.route('/restaurants/<restaurant_id>/working-hours', methods=['GET'])
@auth
def load_add_working_hours(restaurant_id: str):
    return render_template('restaurant/working_hours/add_working_hours.html', restaurant_id=restaurant_id)


@main.route('/restaurants/<restaurant_id>/working-hours', methods=['POST'])
@auth
def add_working_hours(restaurant_id: str):
    restaurant = RestaurantRepository().load(UUID(restaurant_id))
    if not restaurant:
        return make_response('Restaurant not found', 404)

    days_of_week = request.form.getlist('day_of_week[]')
    opening_times = request.form.getlist('opening_time[]')
    closing_times = request.form.getlist('closing_time[]')
    working_hours = []
    for i, day in enumerate(days_of_week):
        opening_time = datetime.strptime(opening_times[i], "%H:%M").time()
        closing_time = datetime.strptime(closing_times[i], "%H:%M").time()
        working_hour = WorkingHour(id=uuid.uuid4(), restaurant_id=restaurant.id, day_of_week=int(day),
                                   opening_time=opening_time, closing_time=closing_time)
        working_hours.append(working_hour)

    WorkingHourRepository().add_all(working_hours)

    response = make_response()
    response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant.id)
    return response
