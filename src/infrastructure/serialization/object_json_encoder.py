from datetime import datetime, date
from enum import Enum
from json import JSONEncoder
from uuid import UUID


class ObjectJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.name
        elif isinstance(o, UUID):
            return str(o)
        elif isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, object):
            return o.__dict__
        else:
            raise Exception("Unsupported type serialization {}".format(o.__class__))
