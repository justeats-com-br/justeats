from pytest import fixture

from src.users.domain.model.user_repository import UserRepository, UserTable
from test.integration_test import IntegrationTest
from test.users.domain.model.user_factory import UserFactory, UserTableFactory


class TestUserRepository(IntegrationTest):
    @fixture
    def repository(self):
        return UserRepository()

    def test_should_add_user(self, session, repository):
        user = UserFactory()

        repository.add(user)

        result = session.query(UserTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == user

    def test_should_load_by_email(self, repository):
        users_records = UserTableFactory.create_batch(2)

        result = repository.load_by_email(users_records[0].email)

        assert result == users_records[0].to_domain()
