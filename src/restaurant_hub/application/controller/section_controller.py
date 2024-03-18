import uuid

from flask import render_template, make_response, url_for

from src.catalogs.domain.model.catalog import Catalog
from src.catalogs.domain.model.catalog_repository import CatalogRepository
from src.catalogs.domain.model.section import Section
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.section_service import SectionService
from src.infrastructure.common.utils import get_utcnow
from src.restaurant_hub.application.controller import main, string_form_value, int_form_value
from src.restaurant_hub.infrastructure.auth import auth


@main.route('/restaurants/<restaurant_id>/section', methods=['GET'])
@auth
def load_add_section(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    return render_template('catalog/section.html', restaurant_id=restaurant_id)


@main.route('/restaurants/<restaurant_id>/sections/<section_id>', methods=['GET'])
@auth
def load_update_section_in_restaurant(restaurant_id: str, section_id: str):
    section_id = uuid.UUID(section_id)
    section = SectionRepository().load(section_id)
    catalog = CatalogRepository().load(section.catalog_id)
    return render_template('catalog/section.html', restaurant_id=catalog.restaurant_id, **_to_section_form(section))


@main.route('/restaurants/<restaurant_id>/sections', methods=['POST'])
@auth
def add_section(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    name = string_form_value('name')
    description = string_form_value('description')
    sort_order = int_form_value('sort_order')

    catalog_repository = CatalogRepository()
    catalog = catalog_repository.load_by_restaurant_id(restaurant_id)
    if not catalog:
        catalog = Catalog(id=uuid.uuid4(), restaurant_id=restaurant_id, created_at=get_utcnow(),
                          updated_at=get_utcnow())
        catalog_repository.add(catalog)

    section = Section(id=uuid.uuid4(), catalog_id=catalog.id, name=name, description=description, sort_order=sort_order,
                      created_at=get_utcnow(), updated_at=get_utcnow())
    result = SectionService().add(section)

    if result.is_left():
        return render_template('catalog/partials/add_section_form.html', messages=result.left(),
                               restaurant_id=restaurant_id, **_to_section_form(section))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant_id)
        return response


@main.route('/restaurants/<restaurant_id>/sections', methods=['PATCH'])
@auth
def update_section_in_restaurant(restaurant_id: str):
    restaurant_id = uuid.UUID(restaurant_id)
    id = uuid.UUID(string_form_value('id'))
    section = SectionRepository().load(id)
    name = string_form_value('name')
    description = string_form_value('description')
    sort_order = int_form_value('sort_order')
    section.name = name
    section.description = description
    section.sort_order = sort_order

    result = SectionService().update(section)

    if result.is_left():
        return render_template('catalog/partials/add_section_form.html', messages=result.left(),
                               restaurant_id=restaurant_id, **_to_section_form(section))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_catalog', restaurant_id=restaurant_id)
        return response


def _to_section_form(section: Section) -> dict[str, any]:
    restaurant_form = {
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'sort_order': section.sort_order
    }

    return {k: v for k, v in restaurant_form.items() if v is not None}
