import base64
import contextlib
import functools
import hashlib
import json as json_lib
import os
import time
import typing
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from unittest.mock import MagicMock
from unittest.mock import patch

import ecdsa
import factory
import flask_sqlalchemy
import pytest
import requests_mock
import sqlalchemy as sa
import weasyprint
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from faker import Faker
from flask import Flask
from flask import g
from flask.testing import FlaskClient
from flask_jwt_extended.utils import create_access_token
from requests.auth import _basic_auth_str  # noqa: TID251

import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.mails.testing as mails_testing
import pcapi.core.object_storage.testing as object_storage_testing
import pcapi.core.search.testing as search_testing
import pcapi.core.testing
import pcapi.core.users.models as users_models
from pcapi.celery_tasks.celery import celery_init_app
from pcapi.celery_tasks.config import CELERY_BASE_SETTINGS
from pcapi.core.users import testing as users_testing
from pcapi.db_utils import clean_all_database
from pcapi.db_utils import install_database_extensions
from pcapi.models import db
from pcapi.models import feature
from pcapi.notifications.internal import testing as internal_notifications_testing
from pcapi.notifications.push import testing as push_notifications_testing
from pcapi.notifications.sms import testing as sms_notifications_testing
from pcapi.routes.backoffice import install_routes
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email
from tests.serialization.extended_spec_tree_test import test_extended_spec_tree_blueprint
from tests.serialization.serialization_decorator_test import test_blueprint
from tests.serialization.serialization_decorator_test import test_bookings_blueprint


@dataclass
class SessionStructre:
    engine: None
    connection: None
    transaction: None
    nested: None


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

    with app.app_context():
        app.test_client_class = FlaskLoginClient
        app.config["TESTING"] = True

        @app.teardown_request
        def clean_g_between_requests(exc: BaseException | None = None) -> None:
            g.pop("_login_user", default=None)

        @app.route("/signin/<int:user_id>", methods=["POST"])
        @csrf.exempt
        def signin(user_id: int):
            from flask_login import login_user

            from pcapi.core.users.models import User

            user = db.session.query(User).filter_by(id=user_id).one()

            login_user(user, remember=True)

            return ""

        install_database_extensions()
        run_migrations()
        feature.install_feature_flags()

        install_routes(app)

        yield app


def build_main_app():
    from pcapi.app import app
    from pcapi.flask_app import remove_db_session

    # Some tests fail without this. It's probably because of
    # pytest_flask_sqlalchemy.
    app.teardown_request_funcs[None].remove(remove_db_session)

    @app.teardown_request
    def clean_g_between_requests(exc: BaseException | None = None) -> None:
        g.pop("_login_user", default=None)

    celery_config = {**CELERY_BASE_SETTINGS, "task_always_eager": True}
    app.config.from_mapping(
        CELERY=celery_config,
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
        feature.install_feature_flags()

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
def clear_tests_assets_bucket(settings):
    try:
        Path(settings.LOCAL_STORAGE_DIR / "thumbs" / "mediations").mkdir(parents=True, exist_ok=True)
        yield
    finally:
        object_storage_testing.reset_bucket()


@pytest.fixture()
def clear_tests_invoices_bucket(settings):
    try:
        Path(settings.LOCAL_STORAGE_DIR / "invoices").mkdir(parents=True, exist_ok=True)
        yield
    finally:
        object_storage_testing.reset_bucket()


@pytest.fixture(scope="function")
def clean_database():
    db.session.close()
    yield
    db.session.close()
    clean_all_database()


@pytest.fixture(scope="session")
def _db(app):
    """
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    """
    install_database_extensions()
    run_migrations()

    clean_all_database()

    return db


pcapi.core.testing.register_event_for_query_logger()


@pytest.fixture(name="client")
def client_fixture(app: Flask):
    # for some reason, it seams that keeping the csrf token causes some
    # trouble during tests (backoffice only, api routes do not have the
    # the csrf protection enabled during tests)
    g.pop("csrf_token", default=None)
    g.pop("jwt_data", default=None)
    return TestClient(app.test_client())


@pytest.fixture
def ubble_mocker(settings) -> typing.Callable:
    @contextlib.contextmanager
    def ubble_mock(identification_id: str, response: str, method="get", mocker: requests_mock.Mocker = None) -> None:
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
def ubble_client(app: Flask, settings):
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

    This is for weasyprint, which uses ``urllib.request.open()``.
    """

    def fake_fetch(url_fetcher, url, *args, **kwargs):
        assert url.startswith("https://fonts.googleapis.com/")
        return weasyprint.urls.URLFetcherResponse(
            url,
            body=b"/*Test*/",
            headers={"Content-Type": 'text/css; charset="utf-8"'},
        )

    with patch("weasyprint.urls.URLFetcher.fetch", fake_fetch):
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

    def with_token(self, user) -> "TestClient":
        token = create_access_token(user.email, additional_claims={"user_claims": {"user_id": user.id}})
        self.auth_header = {
            "Authorization": f"Bearer {token}",
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
        content_type: str | None = "application/json",
    ):
        headers = headers or {}
        if raw_json:
            result = self.client.post(
                route,
                data=raw_json,
                content_type=content_type,
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
                route,
                json=json,
                content_type=content_type,
                headers={**self.auth_header, **headers},
                follow_redirects=follow_redirects,
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
        json = json or {}

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
                content_type="application/json",
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
            route,
            json=json,
            content_type="application/json",
            headers={**self.auth_header, **headers},
            follow_redirects=follow_redirects,
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

    def session_transaction(self, *args, **kwargs):
        return self.client.session_transaction(*args, **kwargs)


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
def _features_context():
    from pcapi.core.testing import FeaturesContext

    return FeaturesContext()


@pytest.fixture(name="features")
def features_fixture(request, _features_context):
    from pcapi.models.feature import FeatureToggle

    marker = request.node.get_closest_marker("features")

    if marker:
        if kwargs := marker.kwargs:
            if invalid_features := {feature for feature in kwargs if feature not in FeatureToggle._member_names_}:
                raise ValueError(f"Invalid features to override: {', '.join(invalid_features)}")
            for attr_name, value in kwargs.items():
                setattr(_features_context, attr_name, value)
        else:
            raise ValueError(
                "Invalid usage of `features` marker, missing features to override.\n"
                "Eg. @pytest.mark.features(WIP_ENABLE_NEW_FEATURE=True)"
            )
    yield _features_context

    _features_context.reset()


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
def run_command(app, clean_database):
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


class TestSession(sa.orm.Session):
    """
    dummy adapter to emulate scoped session in tests
    """

    def remove(self):
        try:
            self.close()
        except Exception:
            pass


@pytest.fixture(scope="function")
def db_session(_db, mocker, request, app):
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
        yield None
    else:
        # derivied from sqlalchemy documentation with tweaks to handle flask-sqlalchemy and the scoped_sessions
        # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
        old_session = db.session
        engine = db.engine
        connection = engine.connect()
        transaction = connection.begin()

        # build a non-scoped session to inject our connection (if we try to use the scoped session
        # it will reuse the old session and not use our custom connexion)
        factory = sa.orm.sessionmaker(
            class_=TestSession,
            query_cls=flask_sqlalchemy.query.Query,
        )
        session = factory(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
        db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()
        # resore old session
        db.session = old_session


@pytest.fixture(autouse=True, scope="session")
def set_faker_locale():
    with factory.Faker.override_default_locale("fr_FR"):
        yield


@pytest.fixture(autouse=True)
def prefetch_feature_flags(monkeypatch, _features_context):
    def is_active(self):
        return getattr(_features_context, self.name)

    monkeypatch.setattr(feature.FeatureToggle, "is_active", is_active)
