import sys
from pathlib import Path

from src.infrastructure.queues.sqs_client import SqsClient
from src.infrastructure.topic.sns_client import SnsClient

_project_base = Path(__file__).parent.parent.absolute()  # noqa
sys.path.insert(0, str(_project_base))  # noqa
sys.path.append(str(_project_base / "vendored"))  # noqa

from src.infrastructure.log.logger import Logger
from src.infrastructure.common.config import ENVIRONMENT


class LambdaHandler:
    def __init__(self):
        self.session = None  # in case subclasses need it
        self._logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger(type(self).__module__)
        return self._logger

    def handle(self, event, context):
        """override to implement the specific handler"""
        raise NotImplementedError("Must be implement in a subclass")

    def __call__(self, event, context):
        """actual lambda handler, generic, calls self.handle()"""
        from src.infrastructure.database.connection_factory import Session

        self.session = Session()
        try:
            response = self.handle(event, context)
            if ENVIRONMENT != "TEST":
                self.session.commit()
            SqsClient().flush_messages()
            SnsClient().flush_messages()
            return response if response else ""
        except Exception as exception:  # noqa
            self.logger.exception("Unexpected exception processing event")
            if ENVIRONMENT != "TEST":
                self.session.rollback()
            raise exception
        finally:
            if ENVIRONMENT != "TEST":
                self.session.close()
                self.session = None
