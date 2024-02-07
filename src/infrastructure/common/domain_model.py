from inspect import getfullargspec

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DomainModel:
    _eq_by_id_only = []
    _eq_ignore = []

    def __eq__(self, other):
        if other is None:
            return False

        # do not compare these attributes recursively, only compared by id
        for attr in self._eq_by_id_only:
            attr_val = getattr(self, attr)
            other_attr_val = getattr(other, attr)

            if attr_val is None:
                if other_attr_val is not None:
                    return False
                continue

            if attr_val.id != other_attr_val.id:
                return False

        # compare all other attributes
        for attr, val in self.__dict__.items():
            if attr in self._eq_by_id_only or attr in self._eq_ignore:
                continue
            if val != getattr(other, attr):
                return False

        return True

    def __repr__(self):
        missing = object()
        kwargs = ', '.join(f"{arg}={getattr(self, arg)!r}"
                           for arg in getfullargspec(self.__init__).args[1:]
                           if getattr(self, arg, missing) is not missing
                           )
        return f"{self.__class__.__name__}({kwargs})"
