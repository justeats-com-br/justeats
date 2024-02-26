from pytest import fixture

from src.catalogs.domain.model.catalog_repository import CatalogRepository, CatalogTable
from test.catalogs.domain.model.catalog_factory import CatalogFactory, CatalogTableFactory
from test.integration_test import IntegrationTest
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.users.domain.model.user_factory import UserTableFactory


class TestCatalogRepository(IntegrationTest):
    @fixture
    def repository(self):
        return CatalogRepository()

    def test_should_add_catalog(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogFactory(restaurant_id=restaurant.id)

        repository.add(catalog)

        result = session.query(CatalogTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == catalog

    def test_should_load_by_restaurant_id(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id)
        other_restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        other_catalog = CatalogTableFactory.create(restaurant_id=other_restaurant.id).to_domain()

        result = repository.load_by_restaurant_id(restaurant.id)

        assert result == catalog

    def test_should_load(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id)

        result = repository.load(catalog.id)

        assert result == catalog
