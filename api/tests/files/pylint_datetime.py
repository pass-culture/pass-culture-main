"""This is a test file for our checker in `pcapi.utils.pylint`.

This file is NOT run by pytest, which is why it does not contain any
assertion.
"""


def test_calls_to_datetime_now():
    variable.now()
    datetime.datetime.utcnow()
    datetime.datetime.now()  # should yield a warning

    datetime.utcnow()
    datetime.now()  # should yield a warning
    a = datetime.now()  # should yield a warning
    func(datetime.now())  # should yield a warning
    func(arg=datetime.now())  # should yield a warning


def test_access_to_datetime_now_function():
    variable.now
    datetime.datetime.utcnow
    datetime.datetime.now  # should yield a warning

    datetime.utcnow
    datetime.now  # should yield a warning
    a = datetime.now  # should yield a warning
    func(datetime.now)  # should yield a warning
    func(arg=datetime.now)  # should yield a warning
