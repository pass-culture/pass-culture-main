import collections.abc
import contextlib
import functools
import math
import types
import typing

import flask
import pytest
import sqlalchemy.engine
import sqlalchemy.event
import sqlalchemy.orm

from pcapi import settings
from pcapi.models import Model
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
            f"{len(queries)} queries executed, {expected_n_queries} expected\nCaptured queries were:\n{details}"
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
    if statement.startswith("SAVEPOINT") or statement.startswith("RELEASE SAVEPOINT") or statement == "SELECT NOW()":
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


class SettingsContext:
    def __init__(self) -> None:
        # Use `object.__setattr__` because `__setattr__` method is overriden
        object.__setattr__(self, "_initial_settings", {})

    def __setattr__(self, attr_name: str, value: typing.Any) -> None:
        self._initial_settings[attr_name] = getattr(settings, attr_name)
        setattr(settings, attr_name, value)

    def __getattr__(self, attr_name: str) -> typing.Any:
        return getattr(settings, attr_name)

    def reset(self) -> None:
        for attr_name, value in self._initial_settings.items():
            setattr(settings, attr_name, value)


class FeaturesContext:
    def __init__(self) -> None:
        # Use `object.__setattr__` because `__setattr__` method is overriden
        object.__setattr__(self, "_initial_features", {})

    def __setattr__(self, attr_name: str, value: typing.Any) -> None:
        self._initial_features[attr_name] = (
            db.session.query(Feature).filter(Feature.name == attr_name).with_entities(Feature.isActive).one().isActive
        )
        db.session.query(Feature).filter(Feature.name == attr_name).update({"isActive": value})
        db.session.commit()
        # Clear the feature cache on request if any
        if flask.has_request_context():
            if hasattr(flask.request, "_cached_features"):
                del flask.request._cached_features

    def __getattr__(self, attr_name: str) -> typing.Any:
        return (
            db.session.query(Feature).filter(Feature.name == attr_name).with_entities(Feature.isActive).one().isActive
        )

    def reset(self) -> None:
        for name, status in self._initial_features.items():
            db.session.query(Feature).filter_by(name=name).update({"isActive": status})
            db.session.commit()
        # Clear the feature cache on request if any
        if flask.has_request_context():
            if hasattr(flask.request, "_cached_features"):
                del flask.request._cached_features


@contextlib.contextmanager
def assert_model_count_delta(
    model: Model,
    delta: int,
) -> collections.abc.Generator[None, None, None]:
    start_count = db.session.query(model).count()
    expected_count = start_count + delta

    yield

    end_count = db.session.query(model).count()
    if end_count != expected_count:
        pytest.fail(f"Got {end_count} {model.__class__.__name__} instead of {expected_count}")
