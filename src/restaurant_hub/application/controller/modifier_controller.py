import uuid

from flask import render_template, make_response, url_for

from src.catalogs.domain.model.modifier import Modifier
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.modifier_service import ModifierService
from src.restaurant_hub.application.controller import main, string_form_value
from src.restaurant_hub.infrastructure.auth import auth


@main.route('/products/<product_id>/modifier', methods=['GET'])
@auth
def load_add_modifier_to_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    return render_template('catalog/modifier.html', product=product, section=section)


@main.route('/products/<product_id>/modifiers/<modifier_id>', methods=['GET'])
@auth
def load_update_modifier_in_product(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    modifier_id = uuid.UUID(modifier_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)

    return render_template('catalog/modifier.html', product=product, section=section,
                           **_to_modifier_form(modifier))


@main.route('/products/<product_id>/modifiers', methods=['POST'])
@auth
def add_modifier_to_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    name = string_form_value('name')
    description = string_form_value('description')
    minimum_options = string_form_value('minimum_options')
    maximum_options = string_form_value('maximum_options')
    modifier = Modifier(id=uuid.uuid4(), name=name, description=description, minimum_options=minimum_options,
                        maximum_options=maximum_options, options=[], )

    result = ModifierService().add(product, modifier)

    if result.is_left():
        return render_template('catalog/partials/add_modifier_form.html', messages=result.left(),
                               product=product,
                               **_to_modifier_form(modifier))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=modifier.id)
        return response


@main.route('/products/<product_id>/modifiers', methods=['PATCH'])
@auth
def update_modifier_in_product(product_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    id = uuid.UUID(string_form_value('id'))
    product_modifier = next((modifier for modifier in product.modifiers if modifier.id == id), None)
    if not product_modifier:
        response = make_response()
        response.status_code = 404
        return response
    name = string_form_value('name')
    description = string_form_value('description')
    minimum_options = string_form_value('minimum_options')
    maximum_options = string_form_value('maximum_options')
    product_modifier.name = name
    product_modifier.description = description
    product_modifier.minimum_options = minimum_options
    product_modifier.maximum_options = maximum_options
    result = ModifierService().update(product, product_modifier)

    if result.is_left():
        return render_template('catalog/partials/add_modifier_form.html', messages=result.left(),
                               product=product,
                               **_to_modifier_form(product_modifier))
    else:
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=product_modifier.id)
        return response


def _to_modifier_form(modifier: Modifier) -> dict[str, any]:
    modifier_form = {
        'id': modifier.id,
        'name': modifier.name,
        'description': modifier.description,
        'minimum_options': modifier.minimum_options,
        'maximum_options': modifier.maximum_options,
        'options': modifier.options,
    }

    return {k: v for k, v in modifier_form.items() if v is not None}
