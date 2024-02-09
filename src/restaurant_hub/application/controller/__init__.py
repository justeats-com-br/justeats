from flask import Blueprint

from src.infrastructure.common.config import ENVIRONMENT
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
def inject_environment():
    return dict(ENVIRONMENT=ENVIRONMENT)


from . import index_controller
from . import sign_up_controller
from . import sign_in_controller
from . import recovery_password_controller
