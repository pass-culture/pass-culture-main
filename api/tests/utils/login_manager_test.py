from datetime import datetime
from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.routes.adage.v1.blueprint import adage_v1 as adage_v1_blueprint
from pcapi.routes.adage_iframe.blueprint import adage_iframe as adage_iframe_blueprint
from pcapi.routes.apis import private_api
from pcapi.routes.apis import public_api
from pcapi.routes.auth.blueprint import auth_blueprint
from pcapi.routes.native.blueprint import native_blueprint
from pcapi.routes.pro.blueprint import pro_private_api as pro_private_api_blueprint
from pcapi.routes.public import blueprints as public_blueprint
from pcapi.routes.saml.blueprint import saml_blueprint as saml_blueprint_blueprint


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


@pytest.fixture(name="login_manager")
def app_fixture(pytestconfig):
    with patch("pcapi.utils.login_manager.app"):
        from pcapi.utils import login_manager

        yield login_manager


class DummySession(dict):
    pass


class ManageProSessionTest:
    def test_no_user(self, login_manager):
        with patch("flask.session", DummySession()) as session:
            result = login_manager.manage_pro_session(None)
            assert len(list(session.keys())) == 0
        assert result is None

    def test_beneficiary_user(self, login_manager):
        user = users_factories.BeneficiaryFactory()
        with patch("flask.session", DummySession()) as session:
            result = login_manager.manage_pro_session(user)
            assert len(list(session.keys())) == 0
        assert result is user

    def test_no_blueprint(self, login_manager):
        user = users_factories.ProFactory()

        with patch("flask.request", None), patch("flask.session", DummySession()) as session:
            result = login_manager.manage_pro_session(user)

            assert len(list(session.keys())) == 0
        assert result is user

    @pytest.mark.parametrize(
        "blueprint_name",
        [
            adage_v1_blueprint.name,
            adage_iframe_blueprint.name,
            public_api.name,
            auth_blueprint.name,
            native_blueprint.name,
            public_blueprint.public_api.name,
            public_blueprint.deprecated_v2_prefixed_public_api.name,
            saml_blueprint_blueprint.name,
        ],
    )
    def test_non_pro_route(self, login_manager, blueprint_name):
        user = users_factories.ProFactory()
        request = MagicMock
        request.blueprint = blueprint_name

        with patch("flask.request", request), patch("flask.session", DummySession()) as session:
            result = login_manager.manage_pro_session(user)

            assert len(list(session.keys())) == 0
        assert result is user

    @pytest.mark.parametrize(
        "blueprint_name",
        [
            private_api.name,
            pro_private_api_blueprint.name,
        ],
    )
    def test_valid_blueprint(self, login_manager, blueprint_name):
        user = users_factories.ProFactory()
        request = MagicMock
        request.blueprint = blueprint_name

        now = datetime(2024, 1, 1, 12, 0, 0)
        expected_last_page = now.timestamp()
        expected_last_login = datetime(2024, 12, 30, 12, 0, 0).timestamp()
        session_mock = DummySession()
        session_mock["last_login"] = expected_last_login
        session_mock["last_api_call"] = datetime(2024, 12, 30, 13, 37, 0).timestamp()

        with patch("flask.request", request), patch("flask.session", session_mock) as session:
            with patch("pcapi.utils.login_manager.datetime") as datetime_mock:
                datetime_mock.utcnow.return_value = now
                datetime_mock.fromtimestamp.side_effect = datetime.fromtimestamp

                result = login_manager.manage_pro_session(user)

            assert len(list(session.keys())) == 2
            assert session["last_login"] == expected_last_login
            assert session["last_api_call"] == expected_last_page

        assert result is user

    def test_expired_session(self, login_manager):
        user = users_factories.ProFactory()
        request = MagicMock
        request.blueprint = "pro_private_api"

        now = datetime(2024, 1, 1, 12, 0, 0)
        session_mock = DummySession()
        session_mock["last_login"] = (now - timedelta(days=365)).timestamp()
        session_mock["last_api_call"] = (now - timedelta(days=365)).timestamp()

        with patch("pcapi.utils.login_manager.discard_session") as discard_session:
            with patch("pcapi.utils.login_manager.logout_user") as logout_user:
                with patch("flask.session", session_mock), patch("flask.request", request):
                    result = login_manager.manage_pro_session(user)
                    discard_session.assert_called_once()
                    logout_user.assert_called_once()
        assert result is None


class ComputeProSessionValidityTest:
    def test_newly_connected(self, login_manager):
        last_login = datetime.utcnow()
        last_api_call = datetime.utcnow()

        result = login_manager.compute_pro_session_validity(last_login, last_api_call)

        assert result

    def test_old_connection_not_recently_used(self, login_manager):
        last_login = datetime.utcnow() - timedelta(days=46)
        last_api_call = datetime.utcnow() - timedelta(days=46)

        result = login_manager.compute_pro_session_validity(last_login, last_api_call)

        assert not result

    def test_old_connection_recently_used(self, login_manager):
        last_login = datetime.utcnow() - timedelta(days=46)
        last_api_call = datetime.utcnow() - timedelta(days=3)

        result = login_manager.compute_pro_session_validity(last_login, last_api_call)

        assert result

    def test_connexion_expired_but_still_active(self, login_manager):
        last_login = datetime.utcnow() - timedelta(days=90)
        last_api_call = datetime.utcnow()

        result = login_manager.compute_pro_session_validity(last_login, last_api_call)

        assert result

    def test_connexion_expired_and_not_active(self, login_manager):
        last_login = datetime.utcnow() - timedelta(days=90)
        last_api_call = datetime.utcnow() - timedelta(days=1)

        result = login_manager.compute_pro_session_validity(last_login, last_api_call)

        assert not result

    def test_connexion_expired_but_still_active_older_than_grace_time(self, login_manager):
        last_login = datetime.utcnow() - timedelta(days=91)
        last_api_call = datetime.utcnow()

        result = login_manager.compute_pro_session_validity(last_login, last_api_call)

        assert not result
