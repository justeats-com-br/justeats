from pytest import fixture

from src.restaurants.domain.model.working_hour_repository import WorkingHourRepository, WorkingHourTable
from test.integration_test import IntegrationTest
from test.restaurants.domain.model.restaurant_factory import RestaurantTableFactory
from test.restaurants.domain.model.working_hour_factory import WorkingHourFactory


class TestWorkingHourRepository(IntegrationTest):
    @fixture
    def repository(self):
        return WorkingHourRepository()

    def test_should_add_all_working_hours(self, session, repository):
        restaurant_record = RestaurantTableFactory.create()
        working_hours = WorkingHourFactory.build_batch(2, restaurant_id=restaurant_record.id)

        repository.add_all(working_hours)

        result = session.query(WorkingHourTable).all()
        assert sorted([record.to_domain().id for record in result]) == sorted(
            [working_hour.id for working_hour in working_hours])
