from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.google_secret_manager import Secret
from pcapi.connectors.google_secret_manager import SecretManagerException
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.sessions import _common
from pcapi.core.users.sessions import delete_expired_sessions
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now


REDIS_KEY = "test:configure_session_keys"

pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


class DeleteExpiredSessionsTest:
    def test_delete_expired_sessions(self):
        user = users_factories.BaseUserFactory()
        valid_session = users_factories.UserSessionFactory(user=user)
        users_factories.UserSessionFactory(user=user, expirationDatetime=get_naive_utc_now() - timedelta(days=1))

        delete_expired_sessions()

        assert db.session.query(users_models.UserSession).count() == 1
        assert db.session.query(users_models.UserSession.id).scalar() == valid_session.id


class ConfigureSessionKeysTest:
    def test_with_no_configuration(self, clear_redis):
        with pytest.raises(ValueError):
            _common.configure_session_keys(default_session_key="", session_keys_secret="", redis_key=REDIS_KEY)

    def test_with_only_default_key(self, clear_redis):
        expected_key = "expected_key"
        with patch("pcapi.core.users.sessions._common.flask.current_app") as current_app:
            current_app.config = {}
            _common.configure_session_keys(
                default_session_key=expected_key, session_keys_secret="", redis_key=REDIS_KEY
            )
            assert current_app.config["SECRET_KEY"] == expected_key
            assert "SECRET_KEY_FALLBACKS" not in current_app.config

    def test_with_only_secret_name(self, clear_redis):
        expected_key = "expected_key"
        fallbacks = ["key 1", "key 2"]
        secret_manager_values = [
            Secret(name="3", creation_timestamp=123456, value=expected_key),
            Secret(name="2", creation_timestamp=123455, value=fallbacks[0]),
            Secret(name="1", creation_timestamp=123454, value=fallbacks[1]),
        ]

        secret_manager = MagicMock()
        secret_manager.get_last_secret_versions.return_value = secret_manager_values
        with patch("pcapi.core.users.sessions._common.SecretManagerBackend", return_value=secret_manager):
            with patch("pcapi.core.users.sessions._common.flask.current_app") as current_app:
                current_app.config = {}
                _common.configure_session_keys(
                    default_session_key="", session_keys_secret="key/secret/manager", redis_key=REDIS_KEY
                )

                assert current_app.config["SECRET_KEY"] == expected_key
                assert current_app.config["SECRET_KEY_FALLBACKS"] == fallbacks

    def test_with_only_secret_name_redis_fallback(self, clear_redis):
        expected_key = "expected_key"
        fallbacks = ["key 1", "key 2"]
        clear_redis.hset(
            REDIS_KEY,
            mapping={
                "123456": expected_key,
                "123455": fallbacks[0],
                "123454": fallbacks[1],
            },
        )
        secret_manager = MagicMock()
        secret_manager.get_last_secret_versions.side_effect = SecretManagerException
        with patch("pcapi.core.users.sessions._common.SecretManagerBackend", return_value=secret_manager):
            with patch("pcapi.core.users.sessions._common.flask.current_app") as current_app:
                current_app.config = {}
                _common.configure_session_keys(
                    default_session_key="", session_keys_secret="key/secret/manager", redis_key=REDIS_KEY
                )
                assert current_app.config["SECRET_KEY"] == expected_key
                assert current_app.config["SECRET_KEY_FALLBACKS"] == fallbacks

    def test_with_only_secret_name_no_redis_fallback(self, clear_redis):
        clear_redis.delete(REDIS_KEY)
        secret_manager = MagicMock()
        secret_manager.get_last_secret_versions.side_effect = SecretManagerException
        with patch("pcapi.core.users.sessions._common.SecretManagerBackend", return_value=secret_manager):
            with pytest.raises(ValueError):
                _common.configure_session_keys(
                    default_session_key="", session_keys_secret="key/secret/manager", redis_key=REDIS_KEY
                )

    def test_with_secret_name_and_default_key(self, clear_redis):
        expected_key = "expected_key"
        legacy_key = "legacy key"
        fallbacks = ["key 1", "key 2", legacy_key]
        secret_manager_values = [
            Secret(name="3", creation_timestamp=123456, value=expected_key),
            Secret(name="2", creation_timestamp=123455, value=fallbacks[0]),
            Secret(name="1", creation_timestamp=123454, value=fallbacks[1]),
        ]

        secret_manager = MagicMock()
        secret_manager.get_last_secret_versions.return_value = secret_manager_values
        with patch("pcapi.core.users.sessions._common.SecretManagerBackend", return_value=secret_manager):
            with patch("pcapi.core.users.sessions._common.flask.current_app") as current_app:
                current_app.config = {}
                _common.configure_session_keys(
                    default_session_key=legacy_key, session_keys_secret="key/secret/manager", redis_key=REDIS_KEY
                )

                assert current_app.config["SECRET_KEY"] == expected_key
                assert current_app.config["SECRET_KEY_FALLBACKS"] == fallbacks
