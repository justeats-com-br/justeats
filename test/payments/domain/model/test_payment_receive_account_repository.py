from pytest import fixture

from src.payments.domain.model.payment_receive_account_repository import PaymentReceiveAccountRepository, \
    PaymentReceiveAccountTable
from test.integration_test import IntegrationTest
from test.payments.domain.model.payment_receive_account_factory import PaymentReceiveAccountFactory, \
    PaymentReceiveAccountTableFactory


class TestPaymentReceiveAccountRepository(IntegrationTest):
    @fixture
    def repository(self):
        return PaymentReceiveAccountRepository()

    def test_should_add_payment_receive_account(self, session, repository):
        payment_receive_account = PaymentReceiveAccountFactory()

        repository.add(payment_receive_account)

        result = session.query(PaymentReceiveAccountTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == payment_receive_account

    def test_should_load_by_restaurant(self, session, repository):
        payment_receive_account = PaymentReceiveAccountTableFactory.create()

        result = repository.load_by_restaurant(payment_receive_account.restaurant_id)

        assert result == payment_receive_account

    def test_should_load(self, repository):
        payment_receive_account = PaymentReceiveAccountTableFactory.create()

        result = repository.load(payment_receive_account.id)

        assert result == payment_receive_account

    def test_should_load_by_external_id(self, session, repository):
        payment_receive_account = PaymentReceiveAccountTableFactory.create()

        result = repository.load_by_external_id(payment_receive_account.external_id)

        assert result == payment_receive_account

    def test_should_update(self, session, repository):
        payment_receive_account = PaymentReceiveAccountTableFactory.create(onboarding_completed=False).to_domain()
        payment_receive_account.onboarding_completed = True

        repository.update(payment_receive_account)

        result = session.query(PaymentReceiveAccountTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == payment_receive_account
