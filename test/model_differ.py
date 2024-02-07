import datetime
import enum
import json
import textwrap
import uuid
from enum import Enum
from typing import Mapping
from uuid import UUID

import pytest
from deepdiff import DeepDiff
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.exc import UnmappedInstanceError

from src.infrastructure.common import DomainModel


class SingletonMixin:
    """Generic mixin that can be added to classes to make them singletons"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class _MissingArgumentValue(SingletonMixin):
    """singleton to be used in as default value where None is a valid value"""
    pass


MISSING = _MissingArgumentValue()


class ValuesExtractor:
    """extracts values from mappings based on a list of keys

    A list of keys can be passed, if not 'id' key is used by default.

    Keys can be nested attributes separeted by dot. For example:
        keys=['product.id']

    This helper class can be either called directly or be instantiated first:

        >>> myobj = {'id': '123', 'planet': 'saturn', 'anumber': 42}

        >>> ValuesExtractor(myobj)
        ('123',)

        >>> ValuesExtractor(myobj, keys=['planet', 'anumber'])
        ('saturn', 42)

    If instantiated, it remembers the list of keys internally:

        >>> extractor = ValuesExtractor(keys=['planet'])
        >>> extractor(myobj)
        ('saturn',)


    Useful for sorting:

        >> people = [
         {'id': 'b1a3', 'name': 'John', 'age': 42},
         {'id': 'a8b6', 'name': 'Mary', 'age': 21},
         {'id': 'd4e6', 'name': 'Anne', 'age': 21},
        ]

        >>> pp(sorted(people, key=ValuesExtractor))  # use 'id' by default
        [{'id': 'a8b6', 'name': 'Mary', 'age': 21},
         {'id': 'b1a3', 'name': 'John', 'age': 42},
         {'id': 'd4e6', 'name': 'Anne', 'age': 21}]

        >>> pp(sorted(people, key=ValuesExtractor(keys=['age'])))
        [{'id': 'a8b6', 'name': 'Mary', 'age': 21},
         {'id': 'd4e6', 'name': 'Anne', 'age': 21},
         {'id': 'b1a3', 'name': 'John', 'age': 42}]

        >>> pp(sorted(people, key=ValuesExtractor(keys=['age', 'name'])))
        [{'id': 'd4e6', 'name': 'Anne', 'age': 21},
         {'id': 'a8b6', 'name': 'Mary', 'age': 21},
         {'id': 'b1a3', 'name': 'John', 'age': 42}]

    """

    def __new__(cls, obj=MISSING, *, keys=('id',), single=True,
                missing_ok=False):
        if obj is MISSING:
            return super().__new__(cls)

        instance = cls(keys=keys)
        return instance(obj)

    def __init__(self, obj=MISSING, *, keys=('id',), single=True,
                 missing_ok=False):
        # single: if the returned list of value contains only one value,
        # return the single value directly instead of a tuple of one value
        self.keys = keys
        self.single = len(keys) == 1 and single
        self.missing_ok = missing_ok

    def __call__(self, obj):
        values = self.extract_values(obj)
        if self.single:
            return values[0]
        return values

    @classmethod
    def _extract_value_by_obj_type(cls, obj, key, missing_ok):
        if isinstance(obj, Mapping):
            try:
                return obj[key]
            except KeyError:
                if missing_ok:
                    return None
                raise
        try:
            return getattr(obj, key)
        except AttributeError:
            if missing_ok:
                return None
            raise

    @classmethod
    def _extract_value(cls, obj, key, missing_ok):
        sub_obj = obj
        for nested_key in key.split('.'):
            sub_obj = cls._extract_value_by_obj_type(sub_obj, nested_key,
                                                     missing_ok)
        return sub_obj

    def extract_values(self, obj):
        return tuple(self._extract_value(obj, k, self.missing_ok)
                     for k in self.keys)


_verbose = False


class ModelEncoder(json.JSONEncoder):

    @staticmethod
    def _is_orm_instance(obj):
        try:
            object_mapper(obj)
        except UnmappedInstanceError:
            return False
        return True

    @staticmethod
    def _full_class_name(class_):
        return f"{class_.__class__.__module__}.{class_.__class__.__qualname__}"

    @classmethod
    def _to_dict(cls, obj):
        return {'_class': cls._full_class_name(obj),
                '_data': obj.__dict__}

    def default(self, obj):
        if isinstance(obj, DomainModel) or self._is_orm_instance(obj):
            return self._to_dict(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.name
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.time):
            return obj.isoformat()
        if isinstance(obj, type):
            return repr(obj)

        return super().default(obj)


def to_json(obj, **kwargs):
    try:
        return json.dumps(obj, cls=ModelEncoder, **kwargs)
    except ValueError as e:
        if 'circular reference' in str(e).lower():
            return f"{ModelEncoder._full_class_name(obj)}: {repr(e)}"
        raise


def to_dict(obj):
    # to convert an arbitrary object to dict, shamelessly serialize it to
    # json first and deserialize to dict
    return json.loads(to_json(obj))


def print_diff(obj1, obj2, diff: DeepDiff = None, verbose=False):
    diff_output_lines = []

    def out(line):
        diff_output_lines.append(line)

    def _format(obj):
        return to_json(obj, indent=4)

    def format_diff():
        for type_of_diff, diff_sub in diff.items():
            out(f"\n  {type_of_diff.replace('_', ' ').capitalize()}:")
            if isinstance(diff_sub, Mapping):
                for item, diff_value in diff_sub.items():
                    diff_value_str = _format(diff_value)
                    out(textwrap.indent(f"{item}: {diff_value_str}\n", ' ' * 6))
            else:
                for diff_value in diff_sub:
                    diff_value_str = _format(diff_value)
                    out(textwrap.indent(f"{diff_value_str}\n", ' ' * 6))

    if diff is None:
        diff = DeepDiff(obj1, obj2)

    if verbose:
        out(f"\nObj1: {_format(obj1)}\n")
        out(f"Obj2: {_format(obj2)}\n")
        out('=' * 70)
    out(f"Differences between objects (DeepDiff):")
    format_diff()

    return '\n'.join(diff_output_lines)


def assert_deep_equal(obj1, obj2):
    __tracebackhide__ = True

    if obj1 == obj2:
        return True

    diff = DeepDiff(obj1, obj2, ignore_type_subclasses=True,
                    ignore_type_in_groups=((UUID, str), (Enum, str)))
    global _verbose
    diff_str = print_diff(obj1, obj2, diff=diff, verbose=_verbose)

    if _verbose:
        pytest.fail(f"Objects are different!\n"
                    f"{diff_str}")
    else:
        pytest.fail(f"Objects are different!\n\n"
                    f"{diff_str}\n"
                    f"Use -vv to see full dump of objects")


def assert_deep_equal_dict(obj1, obj2):
    __tracebackhide__ = True
    assert_deep_equal(to_dict(obj1), to_dict(obj2))


def assert_deep_equal_sorted(obj1, obj2, keys=('id',)):
    __tracebackhide__ = True
    obj1_sorted = sorted(obj1, key=ValuesExtractor(keys=keys))
    obj2_sorted = sorted(obj2, key=ValuesExtractor(keys=keys))
    assert_deep_equal(obj1_sorted, obj2_sorted)
