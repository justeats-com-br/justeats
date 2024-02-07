from itertools import islice
from typing import Sequence


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