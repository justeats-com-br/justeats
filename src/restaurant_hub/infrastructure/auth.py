from functools import wraps
from gettext import gettext

from flask import request, render_template

from src.infrastructure.common.message import Message, MessageCategory
from src.users.domain.model.user_repository import UserRepository
from src.users.domain.service.auth_service import AuthService


def current_user():
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise Exception('Access token not provided')

    auth_result = AuthService().load_username_by_token(access_token)
    if auth_result.is_right():
        email = auth_result.right()
        user = UserRepository().load_by_email(email)
        if not user:
            raise Exception('User not found')
        return user
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

        auth_result = AuthService().load_username_by_token(access_token)
        if auth_result.is_right():
            return view_func(*args, **kwargs)
        else:
            return render_template('index.html', messages=auth_result.left())

    return wrapper
