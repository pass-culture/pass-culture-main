from __future__ import absolute_import

from time import time as _time, sleep as _sleep


_time_travel = False
_time_offset = 0.0


def start_time_travel():
    """For testing.

    Causes :func:`sleep` to return immediately, but still effect the
    output of :func:`time`.

    """
    global _time_travel
    _time_travel = True


def time():
    return _time() + _time_offset


def sleep(amount):
    global _time_offset
    if _time_travel:
        _time_offset += amount
    else:
        _sleep(amount)
