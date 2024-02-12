from gettext import gettext

from flask import render_template, request, make_response, redirect, url_for

from src.infrastructure.common.message import Message, MessageCategory
from src.restaurant_hub.application.controller import main
from src.restaurant_hub.infrastructure.auth import current_user
from src.users.domain.service.auth_service import AuthService


@main.route('/sign-in', methods=['GET'])
def load_sign_in():
    try:
        user = current_user()
        if user:
            return redirect(url_for('main.load_index'))
    except Exception:
        pass

    message = None
    if request.args.get('message') == 'password_updated':
        message = Message(
            category=MessageCategory.INFO,
            target='password',
            message=gettext('Your password has been updated. You can sign in now.'),
            key='password_updated'
        )

    return render_template('sign_in/sign_in.html', message=message)


@main.route('/sign-in', methods=['POST'])
def sign_in():
    email = request.form.get('email')
    password = request.form.get('password')
    result = AuthService().login(email, password)
    if result.is_right():
        (token, refresh_token) = result.right()
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_add_restaurant')
        response.set_cookie('access_token', token)
        response.set_cookie('refresh_token', refresh_token)
        response.set_cookie('email', email)
        return response
    else:
        return render_template('sign_in/partials/sign_in_form.html', messages=result.left(), email=email,
                               password=password)


@main.route('/sign-out', methods=['GET'])
def sign_out():
    response = make_response(redirect(url_for('main.load_sign_in')))
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    response.set_cookie('email', '', expires=0)
    return response
