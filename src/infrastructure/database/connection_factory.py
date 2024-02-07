from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.infrastructure.common.config import get_key, ENVIRONMENT

_database_url = 'postgresql://{}:{}@{}:{}/{}'.format(get_key('db_user'), get_key('db_password'), get_key('db_host'),
                                                     get_key('db_port'), get_key('db_name'))
_engine = create_engine(_database_url, poolclass=NullPool, connect_args={'connect_timeout': 5})
_factory = sessionmaker(bind=_engine)
if ENVIRONMENT == 'TEST':
    Session = scoped_session(sessionmaker(bind=_engine), scopefunc=lambda: 'test')
else:
    Session = scoped_session(sessionmaker(bind=_engine))
