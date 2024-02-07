from functools import wraps

from flask import request, render_template
from flask_babel import gettext

from src.infrastructure.common.message import MessageCategory, Message
from src.users.domain.service.auth_service import AuthService


def current_user_id():
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise Exception('Access token not provided')

    auth_result = AuthService().load_id_by_token(access_token)
    if auth_result.is_right():
        return auth_result.right()
    else:
        raise Exception('Invalid access token')


def auth(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get('access_token')
        if not access_token:
            return render_template('index.html', messages=[Message(
                category=MessageCategory.VALIDATION,
                target='access_token',
                message=gettext('Access token not provided'),
                key='access_token_not_provided'
            )])

        auth_result = AuthService().load_id_by_token(access_token)
        if auth_result.is_right():
            return view_func(*args, **kwargs)
        else:
            return render_template('index.html', messages=auth_result.left())

    return wrapper
