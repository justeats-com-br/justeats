from enum import Enum
from inspect import getfullargspec
from typing import List, Any


class MessageCategory(Enum):
    INFO = 'INFO'
    VALIDATION = 'VALIDATION'


class Message:
    def __init__(self, category: MessageCategory, target: str, message: str, key: str, args: List[Any] = None):
        self.category = category
        self.message = message
        self.target = target
        self.key = key
        self.args = args

    def __eq__(self, other):
        return self.category == other.category \
            and self.message == other.message \
            and self.target == other.target \
            and self.key == other.key \
            and self.args == other.args

    def __repr__(self):
        missing = object()
        kwargs = ', '.join(f"{arg}={getattr(self, arg)!r}"
                           for arg in getfullargspec(self.__init__).args[1:]
                           if getattr(self, arg, missing) is not missing
                           )
        return f"{self.__class__.__name__}({kwargs})"
