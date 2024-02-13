from flask import Blueprint

from src.infrastructure.common.config import ENVIRONMENT, get_key
from src.infrastructure.database.connection_factory import Session

main = Blueprint('main', __name__)


@main.teardown_request
def closeDatabaseSession(e):
    if ENVIRONMENT != 'TEST':
        if e is not None:
            Session().rollback()
        else:
            Session().commit()


@main.context_processor
def inject_environment_variables():
    return dict(ENVIRONMENT=ENVIRONMENT, PLACES_API_KEY=get_key('PLACES_API_KEY'))


from . import index_controller
from . import sign_up_controller
from . import sign_in_controller
from . import recovery_password_controller
from . import restaurant_controller
