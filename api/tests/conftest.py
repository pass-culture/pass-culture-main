import base64
import contextlib
import functools
import hashlib
import json as json_lib
import os
from pathlib import Path
from pprint import pprint
import sys
import time
import typing
from unittest.mock import MagicMock
from unittest.mock import patch
import urllib.parse

from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import ecdsa
from faker import Faker
from flask import Flask
from flask import g
from flask.testing import FlaskClient
from flask_jwt_extended.utils import create_access_token
import pytest
from requests.auth import _basic_auth_str  # pylint: disable=wrong-requests-import
import requests_mock
import sqlalchemy as sa

from pcapi.celery_tasks.celery import celery_init_app
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.mails.testing as mails_testing
import pcapi.core.object_storage.testing as object_storage_testing
import pcapi.core.search.testing as search_testing
import pcapi.core.testing
from pcapi.core.users import testing as users_testing
import pcapi.core.users.models as users_models
from pcapi.install_database_extensions import install_database_extensions
from pcapi.models import db
from pcapi.models.feature import install_feature_flags
from pcapi.notifications.internal import testing as internal_notifications_testing
from pcapi.notifications.push import testing as push_notifications_testing
from pcapi.notifications.sms import testing as sms_notifications_testing
from pcapi.repository.clean_database import clean_all_database
from pcapi.routes.backoffice import install_routes
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email
from tests.serialization.extended_spec_tree_test import test_extended_spec_tree_blueprint
from tests.serialization.serialization_decorator_test import test_blueprint
from tests.serialization.serialization_decorator_test import test_bookings_blueprint


if typing.TYPE_CHECKING:
    from _pytest.config import Config as PytestConfig
    from _pytest.nodes import Item


def run_migrations():
    from pcapi import settings as pcapi_settings

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", pcapi_settings.DATABASE_URL)
    command.upgrade(alembic_cfg, "pre@head")
    command.upgrade(alembic_cfg, "post@head")


def pytest_configure(config):
    if config.getoption("capture") == "no":
        TestClient.WITH_DOC = True


def build_backoffice_app():
    from flask_login import FlaskLoginClient

    from pcapi.backoffice_app import app
    from pcapi.backoffice_app import csrf
    from pcapi.flask_app import remove_db_session

    # Some tests fail without this. It's probably because of
    # pytest_flask_sqlalchemy.
    app.teardown_request_funcs[None].remove(remove_db_session)
    # Since sqla1.4, in tests teardown, all nested transactions (the way to handle 'savepoints') are closed recursively.
    # But in some tests, there are more recursions than the default accepted number (1000)
    sys.setrecursionlimit(3000)

    with app.app_context():
        from pcapi.utils import login_manager

        app.test_client_class = FlaskLoginClient
        app.config["TESTING"] = True

        @app.route("/signin/<int:user_id>", methods=["POST"])
        @csrf.exempt
        def signin(user_id: int):
            from flask_login import login_user

            from pcapi.core.users.models import User

            user = db.session.query(User).filter_by(id=user_id).one()

            login_user(user, remember=True)
            login_manager.stamp_session(user)

            return ""

        install_database_extensions()
        run_migrations()
        install_feature_flags()

        install_routes(app)

        yield app


def build_main_app():
    from pcapi.app import app
    from pcapi.flask_app import remove_db_session

    # Some tests fail without this. It's probably because of
    # pytest_flask_sqlalchemy.
    app.teardown_request_funcs[None].remove(remove_db_session)
    # Since sqla1.4, in tests teardown, all nested transactions (the way to handle 'savepoints') are closed recursively.
    # But in some tests, there are more recursions than the default accepted number (1000)
    sys.setrecursionlimit(3000)

    app.config.from_mapping(
        CELERY=dict(
            # For testing, tasks are run locally
            task_always_eager=True,
        ),
    )

    celery_init_app(app)

    with app.app_context():
        app.config["TESTING"] = True

        app.register_blueprint(test_blueprint, url_prefix="/test-blueprint")
        # Needed to test that /v2/bookings accepts invalid json
        app.register_blueprint(test_bookings_blueprint, url_prefix="/v2")
        app.register_blueprint(test_extended_spec_tree_blueprint)

        install_database_extensions()
        run_migrations()
        install_feature_flags()

        yield app


@pytest.fixture(scope="session", name="app")
def app_fixture(pytestconfig):
    if pytestconfig.option.markexpr == "backoffice":
        yield from build_backoffice_app()
    else:
        yield from build_main_app()


@pytest.fixture(autouse=True)
def clear_outboxes():
    try:
        yield
    finally:
        internal_notifications_testing.reset_requests()
        mails_testing.reset_outbox()
        push_notifications_testing.reset_requests()
        search_testing.reset_search_store()
        sms_notifications_testing.reset_requests()
        users_testing.reset_sendinblue_requests()
        users_testing.reset_zendesk_requests()
        users_testing.reset_zendesk_sell_requests()
        adage_api_testing.reset_requests()


@pytest.fixture(autouse=True)
def clear_redis(app):
    try:
        yield
    finally:
        app.redis_client.flushdb()


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture()
def clear_tests_assets_bucket(settings):  # pylint: disable=redefined-outer-name
    try:
        Path(settings.LOCAL_STORAGE_DIR / "thumbs" / "mediations").mkdir(parents=True, exist_ok=True)
        yield
    finally:
        object_storage_testing.reset_bucket()


@pytest.fixture()
def clear_tests_invoices_bucket(settings):  # pylint: disable=redefined-outer-name
    try:
        Path(settings.LOCAL_STORAGE_DIR / "invoices").mkdir(parents=True, exist_ok=True)
        yield
    finally:
        object_storage_testing.reset_bucket()


@pytest.fixture(scope="function")
def clean_database():
    yield
    clean_all_database()


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

    clean_all_database()

    return mock_db


pcapi.core.testing.register_event_for_query_logger()


@pytest.fixture(name="client")
def client_fixture(app: Flask):
    # for some reason, it seams that keeping the csrf token causes some
    # trouble during tests (backoffice only, api routes do not have the
    # the csrf protection enabled during tests)
    g.pop("csrf_token", default=None)
    return TestClient(app.test_client())


@pytest.fixture(name="ubble_mock")
def ubble_mock(requests_mock, settings):  # pylint: disable=redefined-outer-name
    """
    Mocks all Ubble requests calls to ease test
    Returns a configured requests mock matcher
    """
    # unsure ?
    from tests.connectors.beneficiaries import ubble_fixtures

    settings.UBBLE_API_URL = "https://api.example.com/"
    settings.UBBLE_CLIENT_ID = "client_id"
    settings.UBBLE_CLIENT_SECRET = "client_secret"

    request_matcher = requests_mock.register_uri(
        "POST",
        "https://api.example.com/identifications/",
        json=ubble_fixtures.UBBLE_IDENTIFICATION_RESPONSE,
        status_code=201,
    )
    yield request_matcher


@pytest.fixture(name="ubble_mock_connection_error")
def ubble_mock_connection_error(requests_mock, settings):  # pylint: disable=redefined-outer-name
    """
    Mocks Ubble request which returns ConnectionError (ex Max retries exceeded, Timeout)
    """

    settings.UBBLE_API_URL = "https://api.example.com/"
    settings.UBBLE_CLIENT_ID = "client_id"
    settings.UBBLE_CLIENT_SECRET = "client_secret"

    request_matcher = requests_mock.register_uri(
        "POST",
        "https://api.example.com/identifications/",
        exc=requests.exceptions.ConnectionError,
    )
    yield request_matcher


@pytest.fixture(name="ubble_mock_http_error_status")
def ubble_mock_http_error_status(requests_mock, settings):  # pylint: disable=redefined-outer-name
    """
    Mocks Ubble request which returns ConnectionError (ex Max retries exceeded, Timeout)
    """
    settings.UBBLE_API_URL = "https://api.example.com/"
    settings.UBBLE_CLIENT_ID = "client_id"
    settings.UBBLE_CLIENT_SECRET = "client_secret"

    request_matcher = requests_mock.register_uri(
        "POST",
        "https://api.example.com/identifications/",
        status_code=401,
    )
    yield request_matcher


@pytest.fixture
def ubble_mocker(settings) -> typing.Callable:  # pylint: disable=redefined-outer-name
    @contextlib.contextmanager
    def ubble_mock(  # pylint: disable=redefined-outer-name
        identification_id: str, response: str, method="get", mocker: requests_mock.Mocker = None
    ) -> None:
        url = f"{settings.UBBLE_API_URL}/identifications/{identification_id}/"

        if mocker is None:
            mocker = requests_mock.Mocker()
            with mocker:
                getattr(mocker, method)(url, text=response)
                yield
        else:
            getattr(mocker, method)(url, text=response)
            yield

    return ubble_mock


@pytest.fixture(name="ubble_client")
def ubble_client(app: Flask, settings):  # pylint: disable=redefined-outer-name
    signing_key = ecdsa.SigningKey.generate()

    public_key = signing_key.verifying_key
    with open(settings.UBBLE_SIGNATURE_KEY_PATH, "wb") as ubble_signature_key_file:
        ubble_signature_key_file.write(public_key.to_pem())

    yield UbbleTestClient(app.test_client(), signing_key)

    if os.path.exists(settings.UBBLE_SIGNATURE_KEY_PATH):
        os.remove(settings.UBBLE_SIGNATURE_KEY_PATH)


@pytest.fixture
def css_font_http_request_mock():
    """Intercept requests to fonts.googleapis.com and return an empty
    string.

    This is for weasyprint, which uses ``urllib.request.urlopen()``.
    """

    class FakeResponse:
        class FakeInfo:
            def __init__(self, filename):
                self.filename = filename

            def get_content_type(self):
                return "text/plain"

            def get_param(self, param):
                if param == "charset":
                    return "utf-8"
                raise NotImplementedError()

            def get_filename(self):
                return self.filename

            def get(self, header):
                if header == "Content-Encoding":
                    return None
                raise NotImplementedError()

        def __init__(self, url, content):
            self.url = url
            self.content = content

        def read(self):
            return self.content

        def info(self):
            return self.FakeInfo("dummy_filename.ext")

        def geturl(self):
            return self.url

    def fake_urlopen(request, *args, **kwargs):
        assert request.host == "fonts.googleapis.com"
        return FakeResponse(request.full_url, content=b"")  # return a bytes-like object to avoid TypeError

    with patch("weasyprint.urls.urlopen", fake_urlopen):
        yield


# Define the CHECK_DATA_LEAKS env variable to assert that no test
# leaks any data. This is useful to detect a missing use of the
# `db_session` fixture.
# The value should be a comma-separated list of full model paths, for
# example:
#     CHECK_DATA_LEAKS=pcapi.core.offers.models.Offer,pcapi.core.bookings.models.Booking pytest
if os.environ.get("CHECK_DATA_LEAKS"):

    @pytest.fixture(scope="function", autouse=True)
    def check_data_leaks(request, app):
        models = {import_string(path.strip()) for path in os.environ["CHECK_DATA_LEAKS"].split(",")}

        counts_before = {model: db.session.query(model).count() for model in models}
        yield
        counts_after = {model: db.session.query(model).count() for model in models}
        leaked_models = ", ".join([model.__name__ for model in models if counts_after[model] != counts_before[model]])
        assert not leaked_models, f"LEAK: {request.function} leaks {leaked_models}"


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
        from pcapi import settings as pcapi_settings

        response = self.post(
            "/users/signin",
            {"identifier": email, "password": pcapi_settings.TEST_DEFAULT_PASSWORD, "captchaToken": "test_token"},
        )
        assert response.status_code == 200

        return self

    def with_bo_session_auth(self, user: users_models.User) -> "TestClient":
        response = self.post(f"/signin/{user.id}")
        assert response.status_code == 200

        return self

    def with_basic_auth(self, email: str) -> "TestClient":
        from pcapi import settings as pcapi_settings

        self.auth_header = {
            "Authorization": _basic_auth_str(email, pcapi_settings.TEST_DEFAULT_PASSWORD),
        }
        return self

    def with_token(self, email: str) -> "TestClient":
        self.auth_header = {
            "Authorization": f"Bearer {create_access_token(email)}",
        }
        return self

    def with_eac_token(self) -> "TestClient":
        from pcapi import settings as pcapi_settings

        self.auth_header = {
            "Authorization": f"Bearer {pcapi_settings.EAC_API_KEY}",
        }
        return self

    def with_explicit_token(self, token: str) -> "TestClient":
        self.auth_header = {
            "Authorization": f"Bearer {token}",
        }
        return self

    def with_adage_token(self, email: str, uai: str, **redactor_information) -> "TestClient":
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=email, uai=uai, **{k: v for k, v in redactor_information.items() if v}
        )
        self.auth_header = {
            "Authorization": f"Bearer {adage_jwt_fake_valid_token}",
        }
        return self

    def delete(self, route: str, headers: dict = None):
        headers = headers or {}
        result = self.client.delete(route, headers={**self.auth_header, **headers})
        self._print_spec("DELETE", route, None, result)
        return result

    def open(self, route: str, *args, **kwargs):
        headers = kwargs.get("headers") or {}
        kwargs["headers"] = self.auth_header | headers
        result = self.client.open(route, *args, **kwargs)
        self._print_spec(kwargs["method"], route, None, result)
        return result

    def options(self, route: str, headers: dict = None):
        headers = headers or {}
        result = self.client.options(route, headers={**self.auth_header, **headers})
        self._print_spec("OPTIONS", route, None, result)
        return result

    def get(self, route: str, params=None, headers=None):
        headers = headers or {}
        kwargs = {}
        if params:
            kwargs["query_string"] = urllib.parse.urlencode(params)
        result = self.client.get(
            route,
            headers={**self.auth_header, **headers},
            **kwargs,
        )
        self._print_spec("GET", route, None, result)
        return result

    def get_with_invalid_json_body(self, route: str, headers=None, raw_json=None):
        headers = headers or {}
        result = self.client.get(
            route,
            data=raw_json,
            content_type="application/json",
            headers={**self.auth_header, **headers},
        )
        self._print_spec("GET", route, raw_json, result)
        return result

    def post(
        self,
        route: str,
        json: dict = None,
        raw_json: str = None,
        form: dict = None,
        files: dict = None,
        headers: dict = None,
        follow_redirects: bool = False,
    ):
        headers = headers or {}
        if raw_json:
            result = self.client.post(
                route,
                data=raw_json,
                content_type="application/json",
                headers={**self.auth_header, **headers},
                follow_redirects=follow_redirects,
            )
        elif form or files:
            result = self.client.post(
                route,
                data=form if form else files,
                headers={**self.auth_header, **headers},
                follow_redirects=follow_redirects,
            )
        else:
            result = self.client.post(
                route, json=json, headers={**self.auth_header, **headers}, follow_redirects=follow_redirects
            )

        self._print_spec("POST", route, json, result)
        return result

    def patch(
        self,
        route: str,
        json: dict = None,
        form: dict = None,
        headers: dict = None,
        follow_redirects: bool = False,
    ):
        headers = headers or {}

        if form:
            result = self.client.patch(
                route,
                data=form,
                headers={**self.auth_header, **headers},
                follow_redirects=follow_redirects,
            )
        else:
            result = self.client.patch(
                route,
                json=json,
                headers={**self.auth_header, **headers},
                follow_redirects=follow_redirects,
            )

        self._print_spec("PATCH", route, json, result)
        return result

    def put(
        self,
        route: str,
        json: dict = None,
        headers: dict = None,
        follow_redirects: bool = False,
    ):
        headers = headers or {}
        result = self.client.put(
            route, json=json, headers={**self.auth_header, **headers}, follow_redirects=follow_redirects
        )
        self._print_spec("PUT", route, json, result)
        return result

    def _print_spec(self, verb: str, route: str, request_body: dict, result: requests.Response):
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


class UbbleTestClient(TestClient):
    def __init__(self, client: FlaskClient, signing_key: ecdsa.SigningKey):
        super().__init__(client)
        self.signing_key = signing_key

    def post(
        self,
        route: str,
        json: dict = None,
        raw_json: str = None,
        form: dict = None,
        files: dict = None,
        headers: dict = None,
        follow_redirects: bool = False,
    ):
        assert json, "only posts using json are supported"
        ubble_signature_header = {"Cko-Signature": self._compute_signature(json)}
        if headers is None:
            headers = {}
        return super().post(route, json, raw_json, form, files, {**ubble_signature_header, **headers}, follow_redirects)

    def _compute_signature(self, json: dict):
        timestamp = time.time()
        signed_payload = (f"{timestamp}:{json_lib.dumps(json)}").encode("utf-8")
        raw_signature = self.signing_key.sign(
            signed_payload,
            hashfunc=hashlib.sha512,
            sigencode=ecdsa.util.sigencode_der,
        )
        signature = base64.b64encode(raw_signature).decode("utf-8")
        return f"{timestamp}:877-test-v1:{signature}"


@pytest.fixture
def features(request):
    from pcapi.core.testing import FeaturesContext
    from pcapi.models.feature import FeatureToggle

    marker = request.node.get_closest_marker("features")
    _features = FeaturesContext()
    if marker:
        if kwargs := marker.kwargs:
            if invalid_features := {feature for feature in kwargs if feature not in FeatureToggle._member_names_}:
                raise ValueError(f"Invalid features to override: {', '.join(invalid_features)}")
            for attr_name, value in kwargs.items():
                setattr(_features, attr_name, value)
        else:
            raise ValueError(
                "Invalid usage of `features` marker, missing features to override.\n"
                "Eg. @pytest.mark.features(WIP_ENABLE_NEW_FEATURE=True)"
            )
    yield _features

    _features.reset()


@pytest.fixture(autouse=True)
def _features_marker(request: pytest.FixtureRequest) -> None:
    marker = request.node.get_closest_marker("features")
    if marker:
        request.getfixturevalue("features")


@pytest.fixture
def settings(request):
    from pcapi.core.testing import SettingsContext

    marker = request.node.get_closest_marker("settings")
    _settings = SettingsContext()

    if marker:
        if kwargs := marker.kwargs:
            for attr_name, value in kwargs.items():
                setattr(_settings, attr_name, value)
        else:
            raise ValueError(
                "Invalid usage of `settings` marker, missing settings to override.\n"
                "Eg. @pytest.mark.settings(ENABLE_SENTRY=False)"
            )
    yield _settings

    _settings.reset()


@pytest.fixture(autouse=True)
def _settings_marker(request: pytest.FixtureRequest) -> None:
    marker = request.node.get_closest_marker("settings")
    if marker:
        request.getfixturevalue("settings")


@pytest.fixture
def run_command(app, clean_database):  # pylint: disable=redefined-outer-name
    from tests.test_utils import run_command as _run_command

    return functools.partial(_run_command, app)


@pytest.hookimpl()
def pytest_collection_finish(session):
    backoffice_routes_dir = Path("tests/routes/backoffice")
    routes_dir = Path("tests/routes")
    BO_matches = [
        session.config.rootdir / backoffice_routes_dir in Path(item.fspath).parents
        for item in session.items
        if session.config.rootdir / routes_dir in Path(item.fspath).parents
    ]
    if any(BO_matches) and not all(BO_matches):
        if not session.config.option.collectonly:
            pytest.exit("You can not run backoffice tests with non backoffice tests")
    if any(BO_matches):
        session.config.option.markexpr = "backoffice"


@pytest.fixture(name="rsa_keys")
def generate_rsa_keys():
    """
    Fixture to generate a pair of RSA private and public keys
    Concerns are puts on performance over security
    This is for tests purposes, DO NOT copy paste this code for production keys.
    """
    private_key = rsa.generate_private_key(public_exponent=3, key_size=1024)
    public_key = private_key.public_key()
    private_key_pem_file = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key_pem_file = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key_pem_file, public_key_pem_file


#################################################################################################################
# BEGIN pytest-flask-sqlalchemy rewrite                                                                         #
# Temporary extract from pytest-flask-sqlalchemy library's sources to allow updating the project's dependencies #
#################################################################################################################


@pytest.fixture(scope="function")
def _transaction(request, _db):
    """
    Create a transactional context for tests to run in.
    """
    # Start a transaction
    connection = _db.engine.connect()
    transaction = connection.begin()

    # Bind a session to the transaction. The empty `binds` dict is necessary
    # when specifying a `bind` option, or else Flask-SQLAlchemy won't scope
    # the connection properly
    session = _db.create_scoped_session(options={"bind": connection, "binds": {}})

    # Make sure the session, connection, and transaction can't be closed by accident in
    # the codebase
    connection.force_close = connection.close
    transaction.force_rollback = transaction.rollback

    connection.close = lambda: None
    transaction.rollback = lambda: None
    session.close = lambda: None

    # Begin a nested transaction (any new transactions created in the codebase
    # will be held until this outer transaction is committed or closed)
    session.begin_nested()

    # Each time the SAVEPOINT for the nested transaction ends, reopen it
    @sa.event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, trans):
        if trans.nested and not trans._parent.nested:
            # ensure that state is expired the way
            # session.commit() at the top level normally does
            session.expire_all()

            session.begin_nested()

    # Force the connection to use nested transactions
    connection.begin = connection.begin_nested

    # If an object gets moved to the 'detached' state by a call to flush the session,
    # add it back into the session (this allows us to see changes made to objects
    # in the context of a test, even when the change was made elsewhere in
    # the codebase)
    @sa.event.listens_for(session, "persistent_to_detached")
    @sa.event.listens_for(session, "deleted_to_detached")
    def rehydrate_object(session, obj):
        session.add(obj)

    @request.addfinalizer
    def teardown_transaction():
        # Delete the session
        session.remove()

        # Rollback the transaction and return the connection to the pool
        transaction.force_rollback()
        connection.force_close()

    return connection, transaction, session


@pytest.fixture(scope="function")
def _engine(request, _transaction, mocker):
    """
    Mock out direct access to the semi-global Engine object.
    """
    connection, _, session = _transaction

    # Make sure that any attempts to call `connect()` simply return a
    # reference to the open connection
    engine = mocker.MagicMock(spec=sa.engine.Engine)

    engine.connect.return_value = connection

    # References to `Engine.dialect` should redirect to the Connection (this
    # is primarily useful for the `autoload` flag in SQLAlchemy, which references
    # the Engine dialect to reflect tables)
    engine.dialect = connection.dialect

    @contextlib.contextmanager
    def begin():
        """
        Open a new nested transaction on the `connection` object.
        """
        with connection.begin_nested():
            yield connection

    # Force the engine object to use the current connection and transaction
    engine.begin = begin
    engine.execute = connection.execute

    # Enforce nested transactions for raw DBAPI connections
    def raw_connection():
        # Start a savepoint
        connection.execute("""SAVEPOINT raw_conn""")

        # Preserve close/commit/rollback methods
        connection.connection.force_close = connection.connection.close
        connection.connection.force_commit = connection.connection.commit
        connection.connection.force_rollback = connection.connection.rollback

        # Prevent the connection from being closed accidentally
        connection.connection.close = lambda: None
        connection.connection.commit = lambda: None
        connection.connection.set_isolation_level = lambda level: None

        # If a rollback is initiated, return to the original savepoint
        connection.connection.rollback = lambda: connection.execute("""ROLLBACK TO SAVEPOINT raw_conn""")

        return connection.connection

    engine.raw_connection = raw_connection

    session.bind = engine

    @request.addfinalizer
    def reset_raw_connection():
        # Return the underlying connection to its original state if it has changed
        if hasattr(connection.connection, "force_rollback"):
            connection.connection.commit = connection.connection.force_commit
            connection.connection.rollback = connection.connection.force_rollback
            connection.connection.close = connection.connection.force_close

    return engine


@pytest.fixture(scope="function")
def db_session(_engine, _transaction, mocker, request):
    """
    Make sure all the different ways that we access the database in the code
    are scoped to a transactional context, and return a Session object that
    can interact with the database in the tests.

    Use this fixture in tests when you would like to use the SQLAlchemy ORM
    API, just as you might use a SQLAlchemy Session object.

    Mock out Session objects (a common way of interacting with the database using
    the SQLAlchemy ORM) using a transactional context.
    """

    # No need for the fixture, `clean_database` will do the job
    if "clean_database" in request.fixturenames:
        return None

    _, _, _session = _transaction

    # Whenever the code tries to access a Flask session, use the Session object
    # instead
    mocker.patch("pcapi.models.db.session", new=_session)

    return _session


#################################################################################################################
# END pytest-flask-sqlalchemy rewrite                                                                           #
#################################################################################################################
