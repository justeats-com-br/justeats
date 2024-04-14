from typing import Optional, List, Tuple
from uuid import UUID

from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message
from src.infrastructure.common.utils import get_utcnow
from src.payments.domain.model.payment_receive_account import PaymentReceiveAccount
from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository
from src.payments.domain.model.payment_receive_account_validator import PaymentReceiveAccountValidator
from src.payments.infrastructure.api.stripe.stripe_client import StripeClient
from src.restaurants.domain.model.restaurant import Restaurant


class PaymentReceiveAccountService:
    def __init__(self,
                 payment_receive_account_validator: Optional[PaymentReceiveAccountValidator] = None,
                 payment_receive_account_repository: Optional[PaymentReceiveAccountRepository] = None,
                 stripe_client: Optional[StripeClient] = None):
        self.payment_receive_account_validator = payment_receive_account_validator or PaymentReceiveAccountValidator()
        self.payment_receive_account_repository = payment_receive_account_repository or PaymentReceiveAccountRepository()
        self.stripe_client = stripe_client or StripeClient()

    def add_for_restaurant(self, restaurant: Restaurant, return_url: str, refresh_url: str) \
            -> Either[List[Message], Tuple[PaymentReceiveAccount, str]]:
        existing_payment_receive_account = self.payment_receive_account_repository.load_by_restaurant(restaurant.id)
        if existing_payment_receive_account:
            onboarding_url = self.stripe_client.generate_onboarding_url(existing_payment_receive_account, return_url,
                                                                        refresh_url)
            return Right((existing_payment_receive_account, onboarding_url))

        messages = self.payment_receive_account_validator.validate_restaurant_for_new_account(restaurant)
        if messages:
            return Left(messages)

        added_stripe_account_id = self.stripe_client.add_payment_receive_account_for_restaurant(restaurant)
        payment_receive_account = PaymentReceiveAccount(id=uuid.uuid4(), restaurant_id=restaurant.id,
                                                        external_id=added_stripe_account_id, created_at=get_utcnow())
        self.payment_receive_account_repository.add(payment_receive_account)

        onboarding_url = self.stripe_client.generate_onboarding_url(payment_receive_account, return_url, refresh_url)
        return Right((payment_receive_account, onboarding_url))

    def complete_onboarding(self, restaurant_id: UUID) -> None:
        payment_receive_account = self.payment_receive_account_repository.load_by_restaurant(restaurant_id)
        if not payment_receive_account:
            raise Exception(f"PaymentReceiveAccount for restaurant_id {restaurant_id} not found")

        payment_receive_account.onboarding_completed = True
        self.payment_receive_account_repository.update(payment_receive_account)
