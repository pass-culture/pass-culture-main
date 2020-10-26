import contextlib
import math

import flask

import factory.alchemy
import pytest
import sqlalchemy.engine
import sqlalchemy.event

# 1. SELECT the user (beneficiary).
# 2. INSERT into the user session table
# 3. RELEASE SAVEPOINT: repository.save() calls `session.commit()`
# 4. SELECT the user again, since the session has been released after
#    the RELEASE SAVEPOINT.
AUTHENTICATION_QUERIES = 4


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        # sqlalchemy_session = pcapi.models.db.session
        sqlalchemy_session = 'ignored'  # see hack in `_save()`
        sqlalchemy_session_persistence = 'commit'

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
        # Factory Boy expects that a model instance can be built with this:
        #
        #    instance = Model(attr1='value1', attr2='value2')
        #
        # But PcObject's constructor does not do that, so we have to
        # call `setattr` manually here.
        #
        # FIXME: PcObject.__init__ should be changed. In fact, we
        # should not use PcObject.populate_from_dict to build model
        # instances from JSON input. Hopefully, this will be handled
        # by the future pydantic-based data validation system.
        obj = model_class()
        for attr, value in kwargs.items():
            setattr(obj, attr, value)
        # The rest of the method if the same as the original.
        session.add(obj)
        session_persistence = cls._meta.sqlalchemy_session_persistence
        if session_persistence == factory.alchemy.SESSION_PERSISTENCE_FLUSH:
            session.flush()
        elif session_persistence == factory.alchemy.SESSION_PERSISTENCE_COMMIT:
            session.commit()
        return obj


@contextlib.contextmanager
def assert_num_queries(expected_n_queries):
    """A context manager that verifies that we do not perform unexpected
    SQL queries.

    Usage (through the fixture of the same name)::

        def test_func(assert_num_queries):
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
        details = '\n'.join(
            _format_sql_query(query, i, len(queries))
            for i, query in enumerate(queries, start=1)
        )
        pytest.fail(
            f"{len(queries)} queries executed, {expected_n_queries} expected\n"
            f"Captured queries were:\n{details}"
        )
    del flask._app_ctx_stack._assert_num_queries


def _format_sql_query(query, i, total):
    # SQLAlchemy inserts '\n' into the generated SQL. We add
    # to padding so that the whole query is properly aligned.
    prefix_length = 3 + int(math.log(total, 10))
    sql = (query['statement'] % query['parameters']).replace('\n', '\n' + ' ' * prefix_length)
    return f'{i}. {sql}'


def _record_end_of_query(statement, parameters, **kwargs):
    """Event handler that records SQL queries for assert_num_queries
    fixture.
    """
    # FIXME (dbaty, 2020-10-23): SQLAlchemy issues savepoints. This is
    # probably due to the way we configure it, which should probably
    # be changed.
    if statement.startswith('SAVEPOINT'):
        return
    # Do not record the query if we're not within the
    # assert_num_queries context manager.
    if not hasattr(flask._app_ctx_stack, '_assert_num_queries'):
        return
    flask._app_ctx_stack._assert_num_queries.append(
        {
            'statement': statement,
            'parameters': parameters,
        }
    )


def register_event_for_assert_num_queries():
    sqlalchemy.event.listen(
        sqlalchemy.engine.Engine,
        'after_cursor_execute',
        _record_end_of_query,
        named=True,
    )
