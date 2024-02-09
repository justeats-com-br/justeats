from flask import render_template, request, make_response, url_for

from src.restaurant_hub.application.controller import main
from src.users.domain.service.auth_service import AuthService


@main.route('/recovery-password', methods=['GET'])
def load_recovery_password():
    return render_template('recovery_password/recovery_password.html')


@main.route('/recovery-password', methods=['POST'])
def recovery_password():
    email = request.form.get('email')
    send_password_recovery_result = AuthService().send_password_recovery(email)

    if send_password_recovery_result.is_left():
        return render_template('recovery_password/partials/recovery_password_form.html',
                               messages=send_password_recovery_result.left(), email=email)
    else:
        return render_template('recovery_password/partials/confirm_recovery_code.html', email=email)


@main.route('/recovery-code', methods=['POST'])
def confirm_recovery_code():
    email = request.form.get('email')
    recovery_code = request.form.get('recovery_code')
    new_password = request.form.get('new_password')
    send_password_recovery_result = AuthService().reset_password(email, recovery_code, new_password)

    if send_password_recovery_result.is_left():
        return render_template('recovery_password/partials/confirm_recovery_code.html',
                               messages=send_password_recovery_result.left(), email=email, recovery_code=recovery_code,
                               new_password=new_password)
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_sign_in', message='password_updated')
        return response
