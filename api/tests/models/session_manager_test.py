import threading
from time import time
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from flask import current_app
from flask import g

from pcapi import settings
from pcapi.models import session_manager


@pytest.fixture(scope="function")
def safe_application():
    from pcapi.models import db

    real_db = db
    engines = current_app.extensions[session_manager.EXTENSION_NAME]
    session = getattr(g, "sqlalchemy_session", None)
    if session:
        del g.sqlalchemy_session

    yield

    if session:
        g.sqlalchemy_session = session
    elif hasattr(g, "sqlalchemy_session"):
        del g.sqlalchemy_session
    real_db.init_app(current_app)
    current_app.extensions[session_manager.EXTENSION_NAME] = engines


class DbClassTest:
    def test_pool_size_from_10_to_1(self, safe_application):
        option_dict = {
            "option1": "foo",
            "pool_size": 10,
        }
        db = session_manager.DbClass(engine_options=option_dict)

        assert option_dict is not db.engine_options
        assert db.engine_options["pool_size"] == 1
        assert option_dict["pool_size"] == 10

    def test_pool_size_from_unset_to_1(self, safe_application):
        option_dict = {
            "option1": "foo",
        }
        db = session_manager.DbClass(engine_options=option_dict)

        assert option_dict is not db.engine_options
        assert db.engine_options["pool_size"] == 1
        assert "pool_size" not in option_dict

    def test_init_app(self, safe_application):
        class FakeApp:
            extensions = {}

        fake_app = FakeApp()

        db = session_manager.DbClass(engine_options={})

        db.init_app(fake_app)
        assert len(fake_app.extensions) == 1
        assert isinstance(fake_app.extensions[session_manager.EXTENSION_NAME], session_manager.EnginesContainer)

    def test_has_open_session_is_true(self, safe_application):
        g.sqlalchemy_session = "foo"
        db = session_manager.DbClass(engine_options={})

        assert db.has_open_session()

    def test_has_open_session_is_False(self, safe_application):
        db = session_manager.DbClass(engine_options={})

        assert not db.has_open_session()

    def test_get_existing_session(self, safe_application):
        session = MagicMock()
        g.sqlalchemy_session = session

        db = session_manager.DbClass(engine_options={})

        assert db.session is session

    def test_get_new_session(self, safe_application):
        db = session_manager.DbClass(engine_options={})
        db.init_app(current_app)

        assert db.session

    def test_set_session(self, safe_application):
        session = MagicMock()
        new_session = MagicMock()
        db = session_manager.DbClass(engine_options={})
        g.sqlalchemy_session = session

        db.session = new_session

        assert db.session is new_session
        session.close.assert_called_once()

    def test_del_session(self, safe_application):
        session = MagicMock()
        db = session_manager.DbClass(engine_options={})
        g.sqlalchemy_session = session

        del db.session

        assert not hasattr(g, "sqlalchemy_session")
        assert db.session is not session
        session.close.assert_called_once()

    def test_remove_session(self, safe_application):
        session = MagicMock()
        db = session_manager.DbClass(engine_options={})
        g.sqlalchemy_session = session

        db.remove_session()

        assert not hasattr(g, "sqlalchemy_session")
        assert db.session is not session
        session.close.assert_called_once()

    def test_remove_none_session(self, safe_application):
        db = session_manager.DbClass(engine_options={})

        # check if we do not raises
        db.remove_session()

    def test_get_engine(self, safe_application):
        expected_engine = MagicMock()
        engine_container = MagicMock()
        engine_container.checkout_engine = MagicMock(return_value=expected_engine)
        current_app.extensions[session_manager.EXTENSION_NAME] = engine_container
        db = session_manager.DbClass(engine_options={"foo": "bar"})

        engine = db.engine

        assert engine is expected_engine
        engine_container.checkout_engine.assert_called_once_with(
            settings.DATABASE_URL,
            foo="bar",
            pool_size=1,
        )


class EnginesContainerTest:
    def test_checkout_engine_no_engine(self):
        thread_id = threading.get_ident()
        engine_container = session_manager.EnginesContainer()
        engine = MagicMock()

        with patch("pcapi.models.session_manager.create_engine", return_value=engine) as create_engine:
            result = engine_container.checkout_engine("database_url", foo="bar")

            create_engine.assert_called_once_with("database_url", foo="bar")
        assert result is engine
        assert engine_container._engines_dict_by_thread_id[thread_id]["engine"] is engine
        assert time() - 0.5 < engine_container._engines_dict_by_thread_id[thread_id]["last_use"] < time() + 0.5

    def test_checkout_engine_engine(self):
        thread_id = threading.get_ident()
        engine = MagicMock()
        engine_container = session_manager.EnginesContainer()
        engine_container._engines_dict_by_thread_id = {thread_id: {"engine": engine, "last_use": 123}}

        with patch("pcapi.models.session_manager.create_engine") as create_engine:
            result = engine_container.checkout_engine("database_url", foo="bar")

            create_engine.assert_not_called()
        assert result is engine
        assert engine_container._engines_dict_by_thread_id[thread_id]["engine"] is engine
        assert time() - 0.5 < engine_container._engines_dict_by_thread_id[thread_id]["last_use"] < time() + 0.5

    def test_destroy_engine_no_engine(self):
        engine_container = session_manager.EnginesContainer()

        # should just not raise
        engine_container.destroy_engine()

    def test_destroy_engine_engine(self):
        thread_id = threading.get_ident()
        engine = MagicMock()
        engine_container = session_manager.EnginesContainer()
        engine_container._engines_dict_by_thread_id = {thread_id: {"engine": engine, "last_use": 123}}

        engine_container.destroy_engine()

        engine.dispose.assert_called_once()
        assert engine_container._engines_dict_by_thread_id == {}
