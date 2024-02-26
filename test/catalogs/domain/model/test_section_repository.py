from pytest import fixture

from src.catalogs.domain.model.section_repository import SectionRepository, SectionTable
from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.section_factory import SectionFactory, SectionTableFactory
from test.integration_test import IntegrationTest
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.users.domain.model.user_factory import UserTableFactory


class TestSectionRepository(IntegrationTest):
    @fixture
    def repository(self):
        return SectionRepository()

    def test_should_add_section(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionFactory(catalog_id=catalog.id)

        repository.add(section)

        result = session.query(SectionTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == section

    def test_should_list_by_catalog_id(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        other_catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        other_section = SectionTableFactory.create(catalog_id=other_catalog.id).to_domain()

        result = repository.list_by_catalog_id(catalog.id)

        assert len(result) == 1
        assert result[0] == section

    def test_should_load(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()

        result = repository.load(section.id)

        assert result == section
