import uuid

from flask import render_template, make_response, url_for

from src.infrastructure.common.config import get_key
from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository
from src.payments.domain.service.payment_receive_account_service import PaymentReceiveAccountService
from src.restaurant_hub.application.controller import main
from src.restaurant_hub.infrastructure.auth import auth
from src.restaurants.domain.model.restaurant_repository import RestaurantRepository


@main.route('/restaurants/<restaurant_id>/payment-receive-account', methods=['GET'])
@auth
def load_add_payment_receive_account_to_restaurant(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    restaurant = RestaurantRepository().load(restaurant_id)
    if not restaurant:
        return make_response('Restaurant not found', 404)

    payment_receive_account = PaymentReceiveAccountRepository().load_by_restaurant(restaurant_id)
    if payment_receive_account and payment_receive_account.onboarding_completed:
        return render_template('payment_receive_account/add_payment_receive_account.html',
                               onboarding_completed=True)

    base_url = get_key('RESTAURANT_HUB_URL')
    return_url = f'{base_url}/restaurants/{restaurant_id}/payment-receive-accounts/onboarding-complete'
    refresh_url = url_for('main.load_add_payment_receive_account_to_restaurant', restaurant_id=restaurant.id,
                          _external=True)
    result = PaymentReceiveAccountService().add_for_restaurant(restaurant, return_url, refresh_url)
    if result.is_left():
        return render_template('payment_receive_account/add_payment_receive_account.html',
                               messages=result.left())
    else:
        (payment_receive_account, onboarding_url) = result.right()
        return render_template('payment_receive_account/add_payment_receive_account.html',
                               onboarding_url=onboarding_url)


@main.route('/restaurants/<restaurant_id>/payment-receive-accounts/onboarding-complete', methods=['GET'])
@auth
def complete_payment_receive_account_onboarding(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    PaymentReceiveAccountService().complete_onboarding(restaurant_id)
    return render_template('payment_receive_account/add_payment_receive_account.html',
                           onboarding_completed=True)
