import enum
import json
import logging
import os
import sys
import traceback
from datetime import datetime


def _get_log_level():
    configured_level = os.environ.get('LOG_LEVEL', 'INFO')
    return logging.getLevelName(configured_level)


class LogLevel(enum.Enum):
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7


class Logger:
    def __init__(self, module):
        self.module = module
        logger = logging.getLogger(module)
        logger.setLevel(_get_log_level())
        self._logger = logger

    def info(self, message, *args, **kwargs):
        self._log(self._logger.info, LogLevel.INFO, message, kwargs, None, *args)

    def error(self, message, *args, **kwargs):
        self._log(self._logger.error, LogLevel.ERROR, message, kwargs, None, *args)

    def exception(self, message, *args, **kwargs):
        kwargs['traceback'] = traceback.format_exc()
        self._log(self._logger.exception, LogLevel.ERROR, message, kwargs, None, *args)

    def debug(self, message, *args, **kwargs):
        self._log(self._logger.debug, LogLevel.DEBUG, message, kwargs, None, *args)

    def warn(self, message, *args, **kwargs):
        self._log(self._logger.warning, LogLevel.WARNING, message, kwargs, None, *args)

    def time(self, parent_type, field_name, time, additional_fields={}):
        log_data = {
            "version": "1.1",
            "host": "lambda",
            "short_message": "{parent_type}.{field_name}: {time} ms".format(
                parent_type=parent_type, field_name=field_name, time=time
            ),
            "parent_type": parent_type,
            "field_name": field_name,
            "time": time,
            "level": LogLevel.INFO.value,
            "timestamp": self._now_in_millis(),
            "_log_type": "application/performance",
        }

        if additional_fields:
            log_data.update(additional_fields)

        exc_info = sys.exc_info()
        self._logger.info(json.dumps(log_data), exc_info=exc_info[0] is not None)

    def _log(self, log_level_function, log_level, message, additional_fields=None, full_message=None, *args):
        additional_fields = additional_fields or {}
        if args:
            short_message = message.format(*args)
        else:
            short_message = message
        inc_tb = additional_fields.pop('include_tb', None)
        log_data = {
            'version': '1.1',
            'host': 'lambda',
            'short_message': short_message,
            'full_message': full_message if full_message else '',
            'timestamp': self._now_in_millis(),
            'level': log_level.value,
            'file': self.module,
            '_log_type': 'application',
        }
        log_data.update(additional_fields)

        full_log_msg = f'{short_message}\n{json.dumps(log_data)}'
        inc_exc = sys.exc_info()[0] is not None
        if inc_tb and not inc_exc:
            log_lines = [
                full_log_msg, '\n',
                'Traceback (manually included, not an exception):', '\n']
            log_lines.extend(traceback.format_stack()[:-2])
            full_log_msg = ''.join(log_lines).rstrip()
        log_level_function(full_log_msg, exc_info=inc_exc)

    def _now_in_millis(self):
        epoch = datetime.utcfromtimestamp(0)
        return (datetime.utcnow() - epoch).total_seconds() * 1000.0


logger = Logger(__name__)
