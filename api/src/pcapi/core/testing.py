import collections
import contextlib
import functools
import math
import os
import traceback
import typing

import flask
import pytest
import sqlalchemy.engine
import sqlalchemy.event
import sqlalchemy.orm

from pcapi import settings
from pcapi.models import db
from pcapi.models.feature import Feature
from pcapi.utils import date as date_utils


# 1. SELECT the user session and the user.
AUTHENTICATION_QUERIES = 1

STACKS_FOLDER = "stacks"


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
    flask.g._query_logger = []
    yield
    queries = flask.g._query_logger.copy()

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
    # Ensures we won't get any extra query from pending data within the sqlalchemy session
    db.session.flush()
    # Flask gracefully provides a global. Flask-SQLAlchemy uses it for
    # the same purpose. Let's do the same.
    flask.g._query_logger = []
    yield
    queries = flask.g._query_logger.copy()
    del flask.g._query_logger

    if len(queries) != expected_n_queries:
        details = "\n".join(_format_sql_query(query, i, len(queries)) for i, query in enumerate(queries, start=1))
        if file_name := _save_traces(queries):
            details += f"\n\n Queries stack traces saved in file {file_name}"
        else:
            details += "\n\n To save each query stack trace call the test with the flag --sql-trace"
        pytest.fail(
            f"{len(queries)} queries executed, {expected_n_queries} expected\nCaptured queries were:\n{details}"
        )


def _save_traces(queries: list[dict]) -> str:
    stacks = [query["stack"] for query in queries if query.get("stack")]

    if not stacks:
        return ""

    os.makedirs(STACKS_FOLDER, exist_ok=True)

    first_frame, name = _extract_test_meta(stacks)
    file_name = f"{STACKS_FOLDER}/{date_utils.get_naive_utc_now().strftime('%Y%m%d%H%M%S')}-{name}.stack"

    with open(file_name, mode="w") as fp:
        for i, stack in enumerate(stacks, start=1):
            # remove sqlalchemy internal at the end of the stack
            for last_frame in range(len(stack) - 1, first_frame, -1):
                if "/site-packages/sqlalchemy/" not in stack[last_frame]:
                    break

            if i != 1:
                fp.write(f"\n\n{'+' * 120}\n\n")
            fp.write(f"{i}.\n")
            fp.write("".join(stack[first_frame : last_frame + 1]))

    return file_name


def _extract_test_meta(stacks: list[str]) -> tuple[int, str]:
    """removes pytest overhead and extracts the test's name"""
    for i in range(len(stacks[0])):
        frame = stacks[0][i]
        if "/api/tests/" not in frame:
            continue
        name = frame.split("\n")[0].split(" ")[-1]
        return i, name
    return 0, "error"


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


def _record_end_of_query(statement: str, parameters: dict, _with_trace: bool = False, **kwargs: dict) -> None:
    """Event handler that records SQL queries for assert_num_queries
    fixture.
    """
    # SQLAlchemy issues savepoints, which we do not want to count in
    # `assert_num_queries`.
    if statement.startswith("SAVEPOINT") or statement.startswith("RELEASE SAVEPOINT") or statement == "SELECT NOW()":
        return
    # Do not record the query if we're not within the
    # assert_num_queries context manager.
    if not hasattr(flask.g, "_query_logger"):
        return
    flask.g._query_logger.append(
        {
            "statement": statement,
            "parameters": parameters,
            "stack": traceback.format_stack()[:-1] if _with_trace else None,
        }
    )


def register_event_for_query_logger(with_trace: bool = False) -> None:
    sqlalchemy.event.listen(
        sqlalchemy.engine.Engine,
        "after_cursor_execute",
        functools.partial(
            _record_end_of_query,
            _with_trace=with_trace,
        ),
        named=True,
    )


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
        object.__setattr__(self, "_initial_settings", {})


class FeaturesCache(collections.UserDict):
    def refresh(self) -> None:
        self.data = {f.name: f.isActive for f in db.session.query(Feature.name, Feature.isActive)}


class FeaturesContext:
    def __init__(self) -> None:
        cached_features = FeaturesCache()
        cached_features.refresh()
        # Use `object.__setattr__` because `__setattr__` method is overriden
        object.__setattr__(self, "_modified_values", {})
        object.__setattr__(self, "_cached_features", cached_features)

    def __setattr__(self, attr_name: str, value: typing.Any) -> None:
        self._modified_values[attr_name] = value
        db.session.query(Feature).filter(Feature.name == attr_name).update({"isActive": value})
        db.session.commit()

    def __getattr__(self, attr_name: str) -> typing.Any:
        return self._modified_values.get(attr_name, self._cached_features[attr_name])

    def refresh_cache(self) -> None:
        cached_features = object.__getattribute__(self, "_cached_features")
        cached_features.refresh()

    def reset(self) -> None:
        values_to_reset = {}
        for name, modified_value in self._modified_values.items():
            cached_value = self._cached_features[name]
            if cached_value != modified_value:
                values_to_reset[name] = cached_value

        features = db.session.query(Feature).filter(Feature.name.in_(list(values_to_reset))).all()
        for feature in features:
            feature.isActive = values_to_reset[feature.name]
            db.session.add(feature)

        if values_to_reset:
            db.session.commit()
        object.__setattr__(self, "_modified_values", {})
