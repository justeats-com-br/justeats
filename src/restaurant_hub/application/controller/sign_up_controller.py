from uuid import uuid4

from flask import render_template, request, make_response, url_for

from src.restaurant_hub.application.controller import main
from src.users.domain.model.user import User, UserType
from src.users.domain.service.user_service import UserService


@main.route('/sign-up', methods=['GET'])
def load_sign_up():
    return render_template('sign_up/sign_up.html')


@main.route('/sign-up', methods=['POST'])
def sign_up():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User(
        id=uuid4(),
        email=email,
        name=name,
        type=UserType.RESTAURANT_OWNER
    )
    sign_up_result = UserService().sign_up(user, password)
    if sign_up_result.is_left():
        response = make_response(
            render_template('sign_up/partials/sign_up_form.html',
                            messages=sign_up_result.left(),
                            email=email,
                            name=name, password=password)
        )
        response.status_code = 400
        return response
    else:
        (user, token, refresh_token) = sign_up_result.right()
        response = make_response()
        response.set_cookie('access_token', token)
        response.set_cookie('refresh_token', refresh_token)
        response.set_cookie('email', email)
        response.headers['HX-Redirect'] = url_for('main.load_add_restaurant')
        return response
