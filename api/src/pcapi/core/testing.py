import contextlib
import functools
import math
import pathlib
import shutil
import tempfile
from unittest import mock

import factory.alchemy
import flask
import pytest
import sqlalchemy.engine
import sqlalchemy.event
import sqlalchemy.orm

from pcapi import settings
from pcapi.models.feature import Feature


# 1. SELECT the user session.
# 2. SELECT the user.
AUTHENTICATION_QUERIES = 2


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        # See comment in _save()
        # sqlalchemy_session = pcapi.models.db.session
        sqlalchemy_session = "ignored"  # see hack in `_save()`
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):
        # FIXME (dbaty, 2020-10-20): pytest-flask-sqlalchemy mocks
        # (replaces) `db.session` to remove the session and rollback
        # changes at the end of each test function (see `_session()`
        # fixture in pytest-flask-sqlalchemy). As such, the session
        # that is used in tests is not the session we defined in
        # `Meta.sqlalchemy_session` above. Because of this, data added
        # through a factory is not rollback'ed. To work around this,
        # here is a hack.
        # This issue is discussed here: https://github.com/jeancochrane/pytest-flask-sqlalchemy/issues/12
        from pcapi.models import db

        session = db.session

        known_fields = {
            prop.key
            for prop in sqlalchemy.orm.class_mapper(model_class).iterate_properties
            if isinstance(prop, (sqlalchemy.orm.ColumnProperty, sqlalchemy.orm.RelationshipProperty))
        }
        unknown_fields = set(kwargs.keys()) - known_fields
        if unknown_fields:
            raise ValueError(
                f"{cls.__name__} received unexpected argument(s): "
                f"{', '.join(sorted(unknown_fields))}. "
                f"Possible arguments are: {', '.join(sorted(known_fields))}"
            )

        return super()._save(model_class, session, *args, **kwargs)

    @classmethod
    def _get_or_create(cls, model_class, session, *args, **kwargs):
        from pcapi.models import db

        # See comment in _save for the reason why we inject the
        # session like this.
        session = db.session
        return super()._get_or_create(model_class, session, *args, **kwargs)


@contextlib.contextmanager
def assert_num_queries(expected_n_queries):
    """A context manager that verifies that we do not perform unexpected
    SQL queries.

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
    flask._app_ctx_stack._assert_num_queries = []
    yield
    queries = flask._app_ctx_stack._assert_num_queries
    if len(queries) != expected_n_queries:
        details = "\n".join(_format_sql_query(query, i, len(queries)) for i, query in enumerate(queries, start=1))
        pytest.fail(
            f"{len(queries)} queries executed, {expected_n_queries} expected\n" f"Captured queries were:\n{details}"
        )
    del flask._app_ctx_stack._assert_num_queries


def _format_sql_query(query, i, total):
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


def _record_end_of_query(statement, parameters, **kwargs):
    """Event handler that records SQL queries for assert_num_queries
    fixture.
    """
    # FIXME (dbaty, 2020-10-23): SQLAlchemy issues savepoints. This is
    # probably due to the way we configure it, which should probably
    # be changed.
    if statement.startswith("SAVEPOINT"):
        return
    # Do not record the query if we're not within the
    # assert_num_queries context manager.
    if not hasattr(flask._app_ctx_stack, "_assert_num_queries"):
        return
    flask._app_ctx_stack._assert_num_queries.append(
        {
            "statement": statement,
            "parameters": parameters,
        }
    )


def register_event_for_assert_num_queries():
    sqlalchemy.event.listen(
        sqlalchemy.engine.Engine,
        "after_cursor_execute",
        _record_end_of_query,
        named=True,
    )


class TestContextDecorator:
    """A base class that can be used for test class and test function
    decorators, or as a context manager within a test.

    Taken from Django and slightly adapted and simplified.
    """

    def enable(self):
        raise NotImplementedError()

    def disable(self):
        raise NotImplementedError()

    def __enter__(self):
        return self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def decorate_class(self, cls):
        decorated_setup_method = getattr(cls, "setup_method", None)
        decorated_teardown_method = getattr(cls, "teardown_method", None)

        def setup_method(inner_self):
            self.enable()
            if decorated_setup_method:
                decorated_setup_method(inner_self)

        def teardown_method(inner_self):
            self.disable()
            if decorated_teardown_method:
                decorated_teardown_method(inner_self)

        cls.setup_method = setup_method
        cls.teardown_method = teardown_method
        return cls

    def decorate_callable(self, func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner

    def __call__(self, decorated):
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

    def __init__(self, **overrides):
        self.overrides = overrides

    def enable(self):
        self.initial_state = {name: getattr(settings, name) for name in self.overrides}
        for name, new_value in self.overrides.items():
            setattr(settings, name, new_value)

    def disable(self):
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

    # FIXME (dbaty, 2020-02-09): the `db_session` fixture does not
    # play well with the decorator when the latter is used on a class:
    # changes made by the decorator (during `setup_method()`) are not
    # seen when in the tests. I should try to fix that.
    CAN_BE_USED_ON_CLASSES = False

    def __init__(self, **overrides):
        self.overrides = overrides

    def enable(self):
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
        # Clear the feature cache on request if any
        if flask.has_request_context():
            if hasattr(flask.request, "_cached_features"):
                flask.request._cached_features = {}  # pylint: disable=assigning-non-slot

    def disable(self):
        for name, status in self.apply_to_revert.items():
            Feature.query.filter_by(name=name).update({"isActive": status})
        # Clear the feature cache on request if any
        if flask.has_request_context():
            if hasattr(flask.request, "_cached_features"):
                flask.request._cached_features = {}  # pylint: disable=assigning-non-slot


def clean_temporary_files(test_function):
    """A decorator to be used around tests that use `tempfile.mkdtemp()`
    and `mkstemp()`. It deletes temporary directories and files upon test
    completion.
    """
    paths = []

    original_mkdtemp = tempfile.mkdtemp
    original_mkstemp = tempfile.mkstemp

    def patched_mkdtemp(*args, **kwargs):
        path = original_mkdtemp(*args, **kwargs)
        paths.append(pathlib.Path(path))
        return path

    def patched_mkstemp(*args, **kwargs):
        res = original_mkstemp(*args, **kwargs)
        paths.append(pathlib.Path(res[1]))
        return res

    def cleanup():
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

    def wrapper():
        try:
            with mock.patch.multiple(tempfile, mkdtemp=patched_mkdtemp, mkstemp=patched_mkstemp):
                test_function()
        finally:
            cleanup()

    return wrapper


@contextlib.contextmanager
def assert_model_count_delta(model, delta):
    start_count = model.query.count()
    expected_count = start_count + delta

    yield

    end_count = model.query.count()
    if end_count != expected_count:
        pytest.fail(f"Got {end_count} {model.__class__.__name__} instead of {expected_count}")
