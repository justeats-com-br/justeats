import re
from typing import Optional

import stripe

from src.infrastructure.common.config import get_key
from src.payments.domain.model.payment_receive_account import PaymentReceiveAccount
from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository
from src.restaurants.domain.model.restaurant import Restaurant
from src.users.domain.model.user_repository import UserRepository


class StripeClient:
    stripe.api_key = get_key('stripe_api_key')

    def __init__(self,
                 payment_receive_account_repository: Optional[PaymentReceiveAccountRepository] = None,
                 user_repository: Optional[UserRepository] = None):
        self.payment_receive_account_repository = payment_receive_account_repository or PaymentReceiveAccountRepository()
        self.user_repository = user_repository or UserRepository()

    def add_payment_receive_account_for_restaurant(self, restaurant: Restaurant) -> str:
        user = self.user_repository.load(restaurant.user_id)
        account = stripe.Account.create(
            type='standard',
            country='br',
            email=user.email,
            # capabilities={
            #     'card_payments': {'requested': True},
            #     'transfers': {'requested': True},
            # },
            business_profile={"url": "https://justeats.com.br/restaurants/" + self._generate_slug(restaurant.name)},
        )
        return account['id']

    def generate_onboarding_url(self, payment_receive_account: PaymentReceiveAccount, return_url: str,
                                refresh_url: str) -> str:
        return stripe.AccountLink.create(
            account=payment_receive_account.external_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )['url']

    def _generate_slug(self, value):
        slug = value.lower()
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'[^\w.-]', '', slug)
        return slug
