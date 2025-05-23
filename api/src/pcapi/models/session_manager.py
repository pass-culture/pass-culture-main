import threading
import time
import typing
from random import randint

import sqlalchemy as sa
from flask import current_app
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SessionBase

from pcapi import settings
from pcapi.models.pc_object import BaseQuery


if typing.TYPE_CHECKING:
    from werkzeug.local import LocalProxy

EXTENSION_NAME = "pcapi-sqlalchemy"


class EnginesContainer:
    """Container to persist the engines and connexion and reuse them for multiple http requests

    This class only exposes three public methods methods, `checkout_engine` and `destroy_engine`
    and `clean_engines`
    All public methods of this class are thread safe
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._engines_dict: dict[int, dict] = dict()

    def _get_engine_dict(self, engine_id: int) -> dict:
        """returns a shallow copy of the current dict to use and update"""
        with self._lock:
            return dict(self._engines_dict.get(engine_id, {}))

    def _update_engine_dict(self, engine_id: int, engine_dict: dict) -> None:
        """update the common dict"""
        with self._lock:
            self._engines_dict[engine_id] = engine_dict

    def _delete_engine_dict(self, engine_id: int) -> None:
        with self._lock:
            engine_dict = self._engines_dict.pop(engine_id, None)
        if engine_dict:
            engine_dict["engine"].dispose()
            del engine_dict["engine"]

    def checkout_engine(self, database_url: str, **engine_options: typing.Any) -> sa.engine.Engine:
        thread_id = threading.get_ident()
        engine_dict = self._get_engine_dict(thread_id)

        if not engine_dict:
            engine = create_engine(database_url, **engine_options)
            engine_dict = {"engine": engine}

        engine_dict["last_use"] = time.time()

        self._update_engine_dict(thread_id, engine_dict)
        return engine_dict["engine"]

    def destroy_engine(self) -> None:
        thread_id = threading.get_ident()
        self._delete_engine_dict(thread_id)

    def clean_engines(self, timeout: int) -> None:
        # TODO rpa 12/06/2025 is it really usefull ? maybe configure connexion timeout instead.
        engines_to_delete = []
        now = time.time()
        with self._lock:
            for engine_id, engine_dict in self._engines_dict.items():
                if "last_use" not in engine_dict or now - engine_dict["last_use"] > timeout:
                    engines_to_delete.append(engine_id)
        for engine_id in engines_to_delete:
            try:
                self._delete_engine_dict(engine_id)
            except Exception:  # if something goes wrong there is nothing we can do about it
                pass


class DbClass:
    """Compatibility class that mimic the one from flask_sqlalchemy"""

    def __init__(self, engine_options: dict) -> None:
        self.Model = declarative_base()
        self.engine_options = dict(engine_options)
        self.session_maker = sessionmaker(query_cls=BaseQuery)

        # TODO rpa 23/05/2025 remove pool_size from the configuration and hard set it to 1
        self.engine_options["pool_size"] = 1

    def init_app(self, app: "LocalProxy") -> None:
        app.extensions[EXTENSION_NAME] = EnginesContainer()  # type: ignore[attr-defined]

    def _get_engines_container(self) -> "EnginesContainer":
        return current_app.extensions[EXTENSION_NAME]

    @property
    def session(self) -> sa.orm.session.Session:
        session = getattr(g, "sqlalchemy_session", None)
        if session is None:
            session = self.session_maker(bind=self.engine)
            g.sqlalchemy_session = session
        return g.sqlalchemy_session

    @session.setter
    def session(self, session: SessionBase) -> None:
        # this feature is ony used for the tests
        self.remove_session()
        g.sqlalchemy_session = session

    @session.deleter
    def session(self) -> None:
        # this feature is ony used for the tests
        self.remove_session()

    @property
    def engine(self) -> sa.engine.Engine:
        engines_container = self._get_engines_container()
        assert settings.DATABASE_URL  # helps mypy
        return engines_container.checkout_engine(settings.DATABASE_URL, **self.engine_options)

    def has_open_session(self) -> bool:
        return hasattr(g, "sqlalchemy_session")

    def remove_session(self) -> None:
        if self.has_open_session():
            self.session.close()
            del g.sqlalchemy_session

    def clean_engines(self) -> None:
        number = randint(0, settings.SQLALCHEMY_ENGINE_CLEAN_PROBABILITY)
        if number == 1:
            engines_container = self._get_engines_container()
            engines_container.clean_engines(settings.SQLALCHEMY_UNUSED_ENGINE_TIMEOUT)
