from pytest import fixture

from src.restaurants.domain.model.delivery_method_repository import DeliveryMethodRepository, DeliveryMethodTable
from test.integration_test import IntegrationTest
from test.restaurants.domain.model.delivery_method_factory import DeliveryMethodFactory, DeliveryMethodTableFactory
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.users.domain.model.user_factory import UserTableFactory


class TestDeliveryMethodRepository(IntegrationTest):
    @fixture
    def repository(self):
        return DeliveryMethodRepository()

    def test_should_load_delivery_method(self, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        delivery_method = DeliveryMethodTableFactory.create(restaurant_id=restaurant.id).to_domain()

        result = repository.load(delivery_method.id)

        assert result == delivery_method

    def test_should_list_by_restaurant(self, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        delivery_method = DeliveryMethodTableFactory.create(restaurant_id=restaurant.id).to_domain()

        result = repository.list_by_restaurant(restaurant.id)

        assert len(result) == 1
        assert result[0] == delivery_method

    def test_should_add_delivery_method(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        delivery_method = DeliveryMethodFactory(restaurant_id=restaurant.id)

        repository.add(delivery_method)

        result = session.query(DeliveryMethodTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == delivery_method

    def test_should_update_delivery_method(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        delivery_method = DeliveryMethodTableFactory.create(restaurant_id=restaurant.id).to_domain()
        delivery_method.delivery_radius = 10

        repository.update(delivery_method)

        result = session.query(DeliveryMethodTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == delivery_method

    def test_should_load_by_restaurant_and_delivery_type(self, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        delivery_method = DeliveryMethodTableFactory.create(restaurant_id=restaurant.id).to_domain()

        result = repository.load_by_restaurant_and_delivery_type(restaurant.id, delivery_method.delivery_type)

        assert result == delivery_method
