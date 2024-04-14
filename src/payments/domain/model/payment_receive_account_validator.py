from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper
from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository
from src.restaurants.domain.model.restaurant import Restaurant


class PaymentReceiveAccountValidator:
    def __init__(self, payment_receive_account_repository: Optional[PaymentReceiveAccountRepository] = None):
        self.payment_receive_account_repository = payment_receive_account_repository or PaymentReceiveAccountRepository()

    def validate_restaurant_for_new_account(self, restaurant: Restaurant) -> List[Message]:
        payment_receive_account_repository = self.payment_receive_account_repository

        class PaymentReceiveAccountValidations(Validator):
            def _validate_unique_payment_receive_account(self, constraint, field, value):
                if value:
                    existing_payment_receive_account = payment_receive_account_repository.load_by_restaurant(
                        value)
                    if existing_payment_receive_account:
                        self._error(field, ErrorDefinition(0, 'unique_payment_receive_account'))
                        self.recent_error.constraint = None

        validation_schema = {
            'id': {'unique_payment_receive_account': True},
        }
        validator = PaymentReceiveAccountValidations(validation_schema, allow_unknown=True)
        validator.validate({
            'id': restaurant.id,
        })

        return MessageMapper.to_messages(validator._errors)
