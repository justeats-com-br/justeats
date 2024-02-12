from pytest import fixture

from src.restaurants.domain.model.restaurant_repository import RestaurantRepository, RestaurantTable
from test.integration_test import IntegrationTest
from test.restaurants.domain.model.restaurant_factory import RestaurantFactory, RestaurantTableFactory


class TestRestaurantRepository(IntegrationTest):
    @fixture
    def repository(self):
        return RestaurantRepository()

    def test_should_add_restaurant(self, session, repository):
        restaurant = RestaurantFactory()

        repository.add(restaurant)

        result = session.query(RestaurantTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == restaurant

    def test_should_load_by_document_number(self, repository):
        restaurants_records = RestaurantTableFactory.create_batch(2)

        result = repository.load_by_document_number(restaurants_records[0].document_number)

        assert result == restaurants_records[0].to_domain()
