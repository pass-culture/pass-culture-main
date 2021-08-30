# isort: skip_file
from functools import wraps
from pathlib import Path
from pprint import pprint
from unittest.mock import MagicMock
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended.utils import create_access_token
import pytest
from requests import Response
from requests.auth import _basic_auth_str

# FIXME (dbaty, 2020-02-08): avoid import loop (that occurs when
# importing `pcapi.core.mails.testing`) when running tests. Remove
# `isort: skip_file` above once fixed.
import pcapi.models
from pcapi import settings
import pcapi.core.mails.testing as mails_testing
import pcapi.core.object_storage.testing as object_storage_testing
import pcapi.core.search.testing as search_testing
import pcapi.core.testing
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.install_database_extensions import install_database_extensions
from pcapi.local_providers.install import install_local_providers
from pcapi.models import db
from pcapi.models.feature import install_feature_flags
from pcapi.notifications.push import testing as push_notifications_testing
from pcapi.notifications.sms import testing as sms_notifications_testing
from pcapi.repository.clean_database import clean_all_database
from pcapi.routes import install_all_routes

from tests.serialization.serialization_decorator_test import test_blueprint


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


def pytest_configure(config):
    if config.getoption("capture") == "no":
        TestClient.WITH_DOC = True


@pytest.fixture(scope="session", name="app")
def app_fixture():
    from pcapi import flask_app

    app = flask_app.app

    # FIXME: some tests fail without this, for example:
    #   - pytest tests/admin/custom_views/offer_view_test.py
    #   - pytest tests/core/fraud/test_api.py
    # Leave an XXX note about why we need that.
    app.teardown_request_funcs[None].remove(flask_app.remove_db_session)

    with app.app_context():
        app.config["TESTING"] = True

        install_all_routes(app)

        app.register_blueprint(test_blueprint, url_prefix="/test-blueprint")

        install_database_extensions()
        run_migrations()
        install_feature_flags()
        install_local_providers()

        yield app


@pytest.fixture(autouse=True)
def clear_outboxes():
    try:
        yield
    finally:
        mails_testing.reset_outbox()
        push_notifications_testing.reset_requests()
        search_testing.reset_search_store()
        sms_notifications_testing.reset_requests()
        users_testing.reset_sendinblue_requests()


@pytest.fixture(autouse=True)
def clear_redis(app):
    try:
        yield
    finally:
        app.redis_client.flushdb()


@pytest.fixture()
def clear_tests_assets_bucket():
    try:
        Path(settings.LOCAL_STORAGE_DIR / "thumbs" / "mediations").mkdir(parents=True, exist_ok=True)
        yield
    finally:
        object_storage_testing.reset_bucket()


def clean_database(f: object) -> object:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return_value = f(*args, **kwargs)
        finally:
            clean_all_database()
        return return_value

    return decorated_function


@pytest.fixture(scope="session")
def _db(app):
    """
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    """
    mock_db = db
    mock_db.init_app(app)
    install_database_extensions()
    run_migrations()
    install_feature_flags()

    install_local_providers()
    clean_all_database()

    return mock_db


pcapi.core.testing.register_event_for_assert_num_queries()


@pytest.fixture()
def assert_num_queries():
    return pcapi.core.testing.assert_num_queries


@pytest.fixture(name="client")
def client_fixture(app: Flask):
    return TestClient(app.test_client())


@pytest.fixture(name="cloud_task_client")
def cloud_task_client_fixture():
    """
    Mock for google.cloud.tasks_v2.CloudTasksClient
    """
    with patch("pcapi.tasks.cloud_task.get_client") as mock_get_client:
        cloud_task_client_mock = MagicMock()
        mock_get_client.return_value = cloud_task_client_mock
        yield cloud_task_client_mock


class TestClient:
    WITH_DOC = False

    def __init__(self, client: FlaskClient):
        self.client = client
        self.auth_header = {}

    def with_session_auth(self, email: str) -> "TestClient":
        response = self.post("/users/signin", {"identifier": email, "password": users_factories.DEFAULT_PASSWORD})
        assert response.status_code == 200
        return self

    def with_basic_auth(self, email: str) -> "TestClient":
        self.auth_header = {
            "Authorization": _basic_auth_str(email, users_factories.DEFAULT_PASSWORD),
        }
        return self

    def with_token(self, email: str) -> "TestClient":
        self.auth_header = {
            "Authorization": f"Bearer {create_access_token(email)}",
        }
        return self

    def with_eac_token(self) -> "TestClient":
        self.auth_header = {
            "Authorization": f"Bearer {settings.EAC_API_KEY}",
        }
        return self

    def delete(self, route: str, headers: dict = None):
        headers = headers or {}
        result = self.client.delete(route, headers={**self.auth_header, **headers})
        self._print_spec("DELETE", route, None, result)
        return result

    def get(self, route: str, headers=None):
        headers = headers or {}
        result = self.client.get(route, headers={**self.auth_header, **headers})
        self._print_spec("GET", route, None, result)
        return result

    def post(self, route: str, json: dict = None, form: dict = None, files: dict = None, headers: dict = None):
        headers = headers or {}
        if form or files:
            result = self.client.post(route, data=form if form else files, headers={**self.auth_header, **headers})
        else:
            result = self.client.post(route, json=json, headers={**self.auth_header, **headers})

        self._print_spec("POST", route, json, result)
        return result

    def patch(self, route: str, json: dict = None, headers: dict = None):
        headers = headers or {}
        result = self.client.patch(route, json=json, headers={**self.auth_header, **headers})
        self._print_spec("PATCH", route, json, result)
        return result

    def put(self, route: str, json: dict = None, headers: dict = None):
        headers = headers or {}
        result = self.client.put(route, json=json, headers={**self.auth_header, **headers})
        self._print_spec("PUT", route, json, result)
        return result

    def _print_spec(self, verb: str, route: str, request_body: dict, result: Response):
        if not TestClient.WITH_DOC:
            return

        print("\n===========================================")
        print("%s :: %s" % (verb, route))
        print("STATUS CODE :: %s" % result.status_code)

        if request_body:
            print("REQUEST BODY")
            pprint(request_body)

        if result.data:
            print("RESPONSE BODY")
            pprint(result.json)

        print("===========================================\n")
