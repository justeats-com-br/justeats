from datetime import datetime, timedelta
from itertools import islice
from typing import Optional, Sequence

from pytz import UTC


def none_to_zero(unit):
    return unit if unit is not None else 0


def _timedelta_from_optional_args(
        microseconds=None, microsecs=None,  # alias
        milliseconds=None, ms=None,  # alias
        seconds=None, secs=None,  # alias
        minutes=None, mins=None,  # alias
        hours=None,
        days=None,
        weeks=None):
    _assert_err_msg = "cannot set both at the same time"
    assert seconds is None or secs is None, _assert_err_msg
    assert microseconds is None or microsecs is None, _assert_err_msg
    assert milliseconds is None or ms is None, _assert_err_msg
    assert minutes is None or mins is None, _assert_err_msg

    return timedelta(
        days=none_to_zero(days),
        seconds=none_to_zero(seconds or secs),
        microseconds=none_to_zero(microseconds or microsecs),
        milliseconds=none_to_zero(milliseconds or ms),
        minutes=none_to_zero(minutes or mins),
        hours=none_to_zero(hours),
        weeks=none_to_zero(weeks),
    )


def tz_aware(dt: Optional[datetime], none_ok=False) -> Optional[datetime]:
    """add tzinfo as UTC if datetime is naive, making it aware"""
    if dt is None:
        if none_ok:
            return None
        else:
            raise ValueError("Cannot make None timezone aware")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def get_utcnow(microseconds=None, microsecs=None,  # alias
               milliseconds=None, ms=None,  # alias
               seconds=None, secs=None,  # alias
               minutes=None, mins=None,  # alias
               hours=None, days=None,
               weeks=None, workdays: int = None):
    """now() as UTC timezone with optional timedelta summed"""

    delta = _timedelta_from_optional_args(
        days=days,
        seconds=seconds, secs=secs,
        microseconds=microseconds, microsecs=microsecs,
        milliseconds=milliseconds, ms=ms,
        minutes=minutes, mins=mins,
        hours=hours,
        weeks=weeks,
    )
    return tz_aware(datetime.utcnow()) + delta


def tz_to_utc(dt: Optional[datetime], none_ok=False) -> Optional[datetime]:
    """convert datetime to UTC timezone"""
    if dt is None:
        if none_ok:
            return None
        else:
            raise ValueError("Cannot convert None to UTC")
    return dt.astimezone(UTC)


def chunks(sequence: Sequence, size: int):
    """generator yields lists of length siz with elements from sequence

    Sample usage:
        >>> my_long_sequence = range(10)
        >>> for chunk in chunks(my_long_sequence, 4):
        ...     print(chunk)
        [0, 1, 2, 3]
        [4, 5, 6, 7]
        [8, 9]
    """
    it = iter(sequence)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
