import collections.abc
import contextlib
import functools
import math
import pathlib
import shutil
import tempfile
import types
import typing
from unittest import mock

import flask
import flask_sqlalchemy
import pytest
import sqlalchemy.engine
import sqlalchemy.event
import sqlalchemy.orm

from pcapi import settings
from pcapi.models import db
from pcapi.models.feature import Feature


# 1. SELECT the user session.
# 2. SELECT the user.
AUTHENTICATION_QUERIES = 2


@contextlib.contextmanager
def assert_no_duplicated_queries() -> collections.abc.Generator[None, None, None]:
    """A context manager that verifies that no SQL statement is run twice
    during the execution of the code in the context to prevent N+1 issues.

    Use assert_num_queries() instead if you want to handle precise cases/exceptions
    where this wrapper doesn't work (for instance, you have a duplicated query ran a constant number of time)

    Note: the feature-flag activation check requests are ignored during this verification.

    Usage:
        def test_func():
            with assert_no_duplicated_queries():
                function_under_test()
    """
    # We record queries with _record_end_of_query and register_event_for_query_logger
    flask._app_ctx_stack._query_logger = []  # type: ignore[attr-defined]
    yield
    queries = flask._app_ctx_stack._query_logger.copy()  # type: ignore[attr-defined]

    statements = [query["statement"] for query in queries if "from feature" not in query["statement"].lower()]

    duplicated_queries = [(query, count) for query, count in collections.Counter(statements).items() if count > 1]
    number_of_duplicated_queries = len(duplicated_queries)
    output = ""
    for query in duplicated_queries:
        output += f"\n {query[1]} times: {query[0]}"
    assert number_of_duplicated_queries == 0, (
        f"{number_of_duplicated_queries} out of {len(statements)} queries are duplicated: \n " + output
    )


@contextlib.contextmanager
def assert_num_queries(expected_n_queries: int) -> collections.abc.Generator[None, None, None]:
    """A context manager that verifies that we do not perform unexpected
    SQL queries.

    Prefer assert_no_duplicated_queries() by default
    Use assert_num_queries() if you want to handle precise cases/exceptions to assert_no_duplicated_queries

    Usage::

        def test_func():
            n_queries = 1   # authentication
            n_queries += 1  # select blobs
            n_queries += 2  # update blobs
            with assert_num_queries(n_queries):
                function_under_test()
    """
    # Flask gracefully provides a global. Flask-SQLAlchemy uses it for
    # the same purpose. Let's do the same.
    flask._app_ctx_stack._query_logger = []  # type: ignore[attr-defined]
    yield
    queries = flask._app_ctx_stack._query_logger.copy()  # type: ignore[attr-defined]

    if len(queries) != expected_n_queries:
        details = "\n".join(_format_sql_query(query, i, len(queries)) for i, query in enumerate(queries, start=1))
        pytest.fail(
            f"{len(queries)} queries executed, {expected_n_queries} expected\n" f"Captured queries were:\n{details}"
        )
    del flask._app_ctx_stack._query_logger  # type: ignore[attr-defined]


def _format_sql_query(query: dict, i: int, total: int) -> str:
    # SQLAlchemy inserts '\n' into the generated SQL. We add padding
    # so that the whole query is properly aligned.
    prefix_length = 3 + int(math.log(total, 10))
    # XXX: ugly work around to handle multiple statements,
    # e.g. `INSERT INTO` with multiple rows.
    try:
        sql = (query["statement"] % query["parameters"]).replace("\n", "\n" + " " * prefix_length)
    except TypeError:
        sql = f"{query['statement']}  -- multiple statement with parameters: {query['parameters']}"
    return f"{i}. {sql}"


def _record_end_of_query(statement: str, parameters: dict, **kwargs: dict) -> None:
    """Event handler that records SQL queries for assert_num_queries
    fixture.
    """
    # SQLAlchemy issues savepoints, which we do not want to count in
    # `assert_num_queries`.
    if statement.startswith("SAVEPOINT") or statement.startswith("RELEASE SAVEPOINT"):
        return
    # Do not record the query if we're not within the
    # assert_num_queries context manager.
    if not hasattr(flask._app_ctx_stack, "_query_logger"):
        return
    flask._app_ctx_stack._query_logger.append(
        {
            "statement": statement,
            "parameters": parameters,
        }
    )


def register_event_for_query_logger() -> None:
    sqlalchemy.event.listen(
        sqlalchemy.engine.Engine,
        "after_cursor_execute",
        _record_end_of_query,
        named=True,
    )


DecoratedClass = typing.TypeVar("DecoratedClass")


class TestContextDecorator:
    """A base class that can be used for test class and test function
    decorators, or as a context manager within a test.

    Taken from Django and slightly adapted and simplified.
    """

    def enable(self) -> None:
        raise NotImplementedError()

    def disable(self) -> None:
        raise NotImplementedError()

    def __enter__(self) -> None:
        return self.enable()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType,
    ) -> None:
        self.disable()

    def decorate_class(self, cls: type[DecoratedClass]) -> type[DecoratedClass]:
        decorated_setup_method = getattr(cls, "setup_method", None)
        decorated_teardown_method = getattr(cls, "teardown_method", None)

        def setup_method(inner_self: DecoratedClass) -> None:
            self.enable()
            if decorated_setup_method:
                decorated_setup_method(inner_self)

        def teardown_method(inner_self: DecoratedClass) -> None:
            self.disable()
            if decorated_teardown_method:
                decorated_teardown_method(inner_self)

        cls.setup_method = setup_method  # type: ignore[attr-defined]
        cls.teardown_method = teardown_method  # type: ignore[attr-defined]
        return cls

    def decorate_callable(self, func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Callable:
            with self:
                return func(*args, **kwargs)

        return inner

    def __call__(self, decorated: typing.Callable) -> typing.Callable:
        if isinstance(decorated, type):
            if not getattr(self, "CAN_BE_USED_ON_CLASSES", True):
                raise TypeError(f"{self.__class__.__name__} cannot be used to decorate a class")
            return self.decorate_class(decorated)
        if callable(decorated):
            return self.decorate_callable(decorated)
        raise TypeError(f"Cannot decorate object {decorated}")


class override_settings(TestContextDecorator):
    """A context manager/function decorator that temporarily changes a
    setting.

    Usage:

        with override_settings(OBJECT_STORAGE_URL="https://example.com/storage"):
            call_some_function()

        @override_settings(
            OBJECT_STORAGE_URL="https://example.com/storage",
            OTHER_SETTING=4,
        ):
        def test_some_function():
            pass  # [...]
    """

    def __init__(self, **overrides: dict[str, typing.Any]) -> None:
        self.overrides = overrides

    def enable(self) -> None:
        self.initial_state = {name: getattr(settings, name) for name in self.overrides}
        for name, new_value in self.overrides.items():
            setattr(settings, name, new_value)

    def disable(self) -> None:
        for name, initial_value in self.initial_state.items():
            setattr(settings, name, initial_value)


class override_features(TestContextDecorator):
    """A context manager that temporarily enables and/or disables features.

    It can also be used as a function decorator.

    Usage:

        with override_features(ENABLE_FROBULATION=False):
            call_some_function()

        @override_features(ENABLE_FROBULATION=True)
        def test_something():
            pass  # [...]
    """

    # The `db_session` fixture does not play well with the decorator
    # when the latter is used on a class: changes made by the
    # decorator (during `setup_method()`) are not seen when in the
    # tests.
    CAN_BE_USED_ON_CLASSES = False

    def __init__(self, **overrides: bool) -> None:
        self.overrides = overrides

    def enable(self) -> None:
        state = dict(
            Feature.query.filter(Feature.name.in_(self.overrides)).with_entities(Feature.name, Feature.isActive).all()
        )
        # Yes, the following may perform multiple SQL queries. It's fine,
        # we will probably not toggle thousands of features in each call.
        self.apply_to_revert = {}
        for name, status in self.overrides.items():
            if status != state[name]:
                self.apply_to_revert[name] = not status
                Feature.query.filter_by(name=name).update({"isActive": status})
                db.session.commit()
        # Clear the feature cache on request if any
        if flask.has_request_context():
            if hasattr(flask.request, "_cached_features"):
                del flask.request._cached_features

    def disable(self) -> None:
        for name, status in self.apply_to_revert.items():
            Feature.query.filter_by(name=name).update({"isActive": status})
            db.session.commit()
        # Clear the feature cache on request if any
        if flask.has_request_context():
            if hasattr(flask.request, "_cached_features"):
                del flask.request._cached_features


def clean_temporary_files(test_function: typing.Callable) -> typing.Callable:
    """A decorator to be used around tests that use `tempfile.mkdtemp()`
    and `mkstemp()`. It deletes temporary directories and files upon test
    completion.
    """
    paths = []

    original_mkdtemp = tempfile.mkdtemp
    original_mkstemp = tempfile.mkstemp

    def patched_mkdtemp(*args: typing.Any, **kwargs: typing.Any) -> str:
        path = original_mkdtemp(*args, **kwargs)
        paths.append(pathlib.Path(path))
        return path

    def patched_mkstemp(*args: typing.Any, **kwargs: typing.Any) -> tuple[typing.Any, ...]:
        res = original_mkstemp(*args, **kwargs)
        paths.append(pathlib.Path(res[1]))
        return res

    def cleanup() -> None:
        tempdir = pathlib.Path(tempfile.gettempdir())
        for path in paths:
            if not path.exists():
                continue
            if tempdir not in path.parents:
                # I doubt it's intended, let's raise an error.
                raise ValueError(f"Temporary file at '{path}' does not belong in {tempdir}")
            if path == pathlib.Path("/"):
                raise ValueError("I'm sorry, Dave. I'm afraid I can't do that")
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> None:
        try:
            with mock.patch.multiple(tempfile, mkdtemp=patched_mkdtemp, mkstemp=patched_mkstemp):
                test_function(*args, **kwargs)
        finally:
            cleanup()

    return wrapper


@contextlib.contextmanager
def assert_model_count_delta(
    model: flask_sqlalchemy.Model,
    delta: int,
) -> collections.abc.Generator[None, None, None]:
    start_count = model.query.count()
    expected_count = start_count + delta

    yield

    end_count = model.query.count()
    if end_count != expected_count:
        pytest.fail(f"Got {end_count} {model.__class__.__name__} instead of {expected_count}")
