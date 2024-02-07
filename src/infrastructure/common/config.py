import configparser
import os

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'TEST').upper()
_config = configparser.ConfigParser()
_config.read(os.path.dirname(__file__) + '/../../../config/config.ini')


def get_key(key):
    env_value = os.environ.get(key.upper())
    if env_value:
        return env_value
    else:
        return _config[ENVIRONMENT.upper()][key.upper()]
