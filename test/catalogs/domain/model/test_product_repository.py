from pytest import fixture

from src.catalogs.domain.model.product_repository import ProductRepository, ProductTable
from test.catalogs.domain.model.catalog_factory import CatalogTableFactory
from test.catalogs.domain.model.product_factory import ProductFactory, ProductTableFactory
from test.catalogs.domain.model.section_factory import SectionTableFactory
from test.integration_test import IntegrationTest
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.users.domain.model.user_factory import UserTableFactory


class TestProductRepository(IntegrationTest):
    @fixture
    def repository(self):
        return ProductRepository()

    def test_should_add_product(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductFactory(section_id=section.id)

        repository.add(product)

        result = session.query(ProductTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == product

    def test_should_update_product(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        product.name = 'new name'

        repository.update(product)

        result = session.query(ProductTable).all()
        assert len(result) == 1
        assert result[0].to_domain() == product

    def test_should_list_by_section_ids(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()
        other_section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        other_product = ProductTableFactory.create(section_id=other_section.id).to_domain()

        result = repository.list_by_section_ids([section.id])

        assert len(result) == 1
        assert result[0] == product
        assert result[0].section_id == section.id

    def test_should_load(self, session, repository):
        user = UserTableFactory.create().to_domain()
        restaurant = RestaurantTableFactory.create(user_id=user.id).to_domain()
        catalog = CatalogTableFactory.create(restaurant_id=restaurant.id).to_domain()
        section = SectionTableFactory.create(catalog_id=catalog.id).to_domain()
        product = ProductTableFactory.create(section_id=section.id).to_domain()

        result = repository.load(product.id)

        assert result == product
