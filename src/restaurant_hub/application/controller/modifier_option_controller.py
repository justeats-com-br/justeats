import uuid

from flask import render_template, make_response, url_for

from src.catalogs.domain.model.modifier import ModifierOption
from src.catalogs.domain.model.product_repository import ProductRepository
from src.catalogs.domain.model.section_repository import SectionRepository
from src.catalogs.domain.service.modifier_option_service import ModifierOptionService
from src.restaurant_hub.application.controller import main, string_form_value, decimal_form_value
from src.restaurant_hub.infrastructure.auth import auth


@main.route('/products/<product_id>/modifiers/<modifier_id>/option', methods=['GET'])
@auth
def load_add_option_to_modifier(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    modifier_id = uuid.UUID(modifier_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
    return render_template('catalog/option.html', product=product, section=section, modifier=modifier)


@main.route('/products/<product_id>/modifiers/<modifier_id>/options', methods=['POST'])
@auth
def add_option_to_modifier(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    modifier_id = uuid.UUID(modifier_id)
    section = SectionRepository().load(product.section_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)

    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
    option = ModifierOption(
        id=uuid.uuid4(),
        name=name,
        description=description,
        price=price,
    )

    result = ModifierOptionService().add(product, modifier_id, option)

    if result.is_left():
        return render_template('catalog/partials/add_option_form.html', messages=result.left(),
                               product=product, section=section, modifier=modifier,
                               **_to_modifier_option_form(option))
    else:
        _, modifier, _ = result.right()
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=modifier.id)
        return response


@main.route('/products/<product_id>/modifiers/<modifier_id>/options/<option_id>', methods=['GET'])
@auth
def load_update_option_in_modifier(product_id: str, modifier_id: str, option_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    section = SectionRepository().load(product.section_id)
    modifier_id = uuid.UUID(modifier_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
    option_id = uuid.UUID(option_id)
    option = next((option for option in modifier.options if option.id == option_id), None)

    return render_template('catalog/option.html', product=product, section=section, modifier=modifier,
                           **_to_modifier_option_form(option))


@main.route('/products/<product_id>/modifiers/<modifier_id>/options', methods=['PATCH'])
@auth
def update_option_in_modifier(product_id: str, modifier_id: str):
    product_id = uuid.UUID(product_id)
    product = ProductRepository().load(product_id)
    modifier_id = uuid.UUID(modifier_id)
    section = SectionRepository().load(product.section_id)
    modifier = next((modifier for modifier in product.modifiers if modifier.id == modifier_id), None)
    id = uuid.UUID(string_form_value('id'))
    option = next((option for option in modifier.options if option.id == id), None)
    if not option:
        response = make_response()
        response.status_code = 404
        return response
    name = string_form_value('name')
    description = string_form_value('description')
    price = int(decimal_form_value('price') * 100) if decimal_form_value('price') else None
    option.name = name
    option.description = description
    option.price = price
    result = ModifierOptionService().update(product, modifier_id, option)

    if result.is_left():
        return render_template('catalog/partials/add_option_form.html', messages=result.left(),
                               product=product, section=section, modifier=modifier,
                               **_to_modifier_option_form(option))
    else:
        _, modifier, _ = result.right()
        response = make_response()
        response.headers['HX-Redirect'] = url_for('main.load_update_modifier_in_product', product_id=product.id,
                                                  modifier_id=modifier.id)
        return response


def _to_modifier_option_form(option: ModifierOption) -> dict[str, any]:
    modifier_form = {
        'id': option.id,
        'name': option.name,
        'description': option.description,
        'price': option.price,
    }

    return {k: v for k, v in modifier_form.items() if v is not None}
