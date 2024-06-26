from unittest.mock import patch

import flask
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.models import api_errors
from pcapi.utils.crypto import check_public_api_key
from pcapi.utils.crypto import hash_password
from pcapi.validation.routes import users_authentifications

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class ApiKeyRequiredTest:
    def _make_app(self):
        app = flask.Flask(__name__)

        @app.route("/test", methods=["GET"])
        @users_authentifications.api_key_required
        def index():
            return "OK"

        # Simulate `routes.error_handlers.generic_error_handlers.restize_api_errors`...
        # without importing the function, which fails because it
        # expects to have a proper Flask app with a context.
        @app.errorhandler(api_errors.ApiErrors)
        def handle_api_errors(error):
            return "", error.status_code

        return app

    @pytest.mark.parametrize(
        "offerer_is_active,expected_response_status",
        [(True, 200), (False, 403)],
    )
    def test_require_api_key(self, offerer_is_active, expected_response_status):
        app = self._make_app()
        client = TestClient(app.test_client())

        offerers_factories.ApiKeyFactory(offerer__isActive=offerer_is_active)
        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        response = client.get("/test", headers=headers)

        assert response.status_code == expected_response_status

    @pytest.mark.parametrize(
        "provider_is_active,expected_response_status",
        [(True, 200), (False, 403)],
    )
    def test_require_active_provider(self, provider_is_active, expected_response_status):
        offerer = offerers_factories.OffererFactory(name="Technical provider")
        provider = providers_factories.ProviderFactory(
            name="Technical provider", localClass=None, isActive=provider_is_active, enabledForPro=True
        )
        offerers_factories.ApiKeyFactory(
            offerer=offerer,
            provider=provider,
        )
        providers_factories.OffererProviderFactory(
            offerer=offerer,
            provider=provider,
        )
        app = self._make_app()
        client = TestClient(app.test_client())

        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        response = client.get("/test", headers=headers)

        assert response.status_code == expected_response_status

    @pytest.mark.parametrize("use_fast_and_insecure_password_hashing_algorithm", [True, False])
    @override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=False)
    @patch("pcapi.utils.crypto.check_public_api_key")
    @patch("pcapi.utils.crypto.hash_public_api_key")
    def test_ff_for_prod_and_testing_env(
        self,
        hash_public_api_key_function,
        check_public_api_key_function,
        use_fast_and_insecure_password_hashing_algorithm,
    ):
        with override_settings(
            USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=use_fast_and_insecure_password_hashing_algorithm
        ):
            api_key = offerers_factories.ApiKeyFactory()
            old_secret = api_key.secret
            if use_fast_and_insecure_password_hashing_algorithm:
                # md5 hashing
                assert not old_secret.decode("utf-8").startswith("$2b$")
                assert not old_secret.decode("utf-8").startswith("$sha3_512$")
            else:
                assert old_secret.decode("utf-8").startswith("$2b$")  # testing that the secret is hashed with bcrypt
            app = self._make_app()
            client = TestClient(app.test_client())
            headers = {"Authorization": "Bearer development_prefix_clearSecret"}
            response = client.get("/test", headers=headers)
            assert response.status_code == 200
            assert api_key.secret.decode("utf-8") == old_secret.decode("utf-8")
            check_public_api_key_function.assert_not_called()
            hash_public_api_key_function.assert_not_called()

    @override_settings(
        USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=False,
    )
    @override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=True)
    def test_old_api_key_update(self, db_session):
        """Test that old api key is updated to the new hashing algorithm"""
        api_key = offerers_factories.ApiKeyFactory()

        api_key.secret = hash_password("clearSecret")
        assert api_key.secret.decode("utf-8").startswith("$2b$")
        app = self._make_app()
        client = TestClient(app.test_client())

        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        response = client.get("/test", headers=headers)
        assert response.status_code == 200
        assert api_key.secret.decode("utf-8").startswith("$sha3_512$")
        assert check_public_api_key("clearSecret", api_key.secret)
        db_session.flush()

    @override_settings(
        USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=False,
    )
    @override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=True)
    @pytest.mark.parametrize("hashcode", ["$2a$12$hashed_password", "$2x$12$hashed_password", "$2y$12$hashed_password"])
    @patch("pcapi.utils.crypto.check_password")
    @patch("pcapi.utils.crypto.check_public_api_key")
    def test_deprecated_hash(self, mock_check_public_api_key, mock_check_password, hashcode):
        api_key = offerers_factories.ApiKeyFactory()
        api_key.secret = f"$2a$12${hashcode}".encode("utf-8")
        app = self._make_app()
        client = TestClient(app.test_client())

        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        client.get("/test", headers=headers)

        mock_check_password.assert_called()
        mock_check_public_api_key.assert_not_called()

    @override_settings(
        USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=True,
    )
    @override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=True)
    def test_unsecure_old_api_key_update(self, db_session):
        """Test that old md5 api key isn't updated to the new hashing algorithm"""
        api_key = offerers_factories.ApiKeyFactory()
        api_key.secret = hash_password("clearSecret")
        app = self._make_app()
        client = TestClient(app.test_client())

        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        response = client.get("/test", headers=headers)
        assert response.status_code == 200
        assert not api_key.secret.decode("utf-8").startswith("$sha3_512$")
        assert check_public_api_key("clearSecret", api_key.secret)
        db_session.flush()

    @override_settings(
        USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=False,
    )
    def test_switching_ff(self, db_session):
        """Test that the hashing algorithm is updated when the feature flag is switched"""
        app = self._make_app()
        client = TestClient(app.test_client())
        with override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=False):
            api_key = offerers_factories.ApiKeyFactory()
            assert api_key.secret.decode("utf-8").startswith("$2b$")

        with override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=True):
            headers = {"Authorization": "Bearer development_prefix_clearSecret"}
            response = client.get("/test", headers=headers)
            assert response.status_code == 200
            db_session.refresh(api_key)
            assert api_key.secret.decode("utf-8").startswith("$sha3_512$")
            assert check_public_api_key("clearSecret", api_key.secret)

        with override_features(WIP_ENABLE_NEW_HASHING_ALGORITHM=False):
            response = client.get("/test", headers=headers)
            assert response.status_code == 200
            assert check_public_api_key("clearSecret", api_key.secret)
