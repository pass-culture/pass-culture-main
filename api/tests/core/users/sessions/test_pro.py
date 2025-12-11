from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users.sessions import _pro
from pcapi.utils import date as date_utils


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


class DummySession(dict):
    pass


class ManageProSessionTest:
    def test_no_user(self):
        with patch("flask.session", DummySession()) as session:
            result = _pro.manage_pro_session(None)
            assert len(list(session.keys())) == 0
        assert result is None

    def test_nominal(self):
        user = users_factories.ProFactory()

        now = datetime(2024, 1, 1, 12, 0, 0)
        expected_last_page = now.timestamp()
        expected_last_login = datetime(2024, 12, 30, 12, 0, 0).timestamp()
        session_mock = DummySession()
        session_mock["last_login"] = expected_last_login
        session_mock["last_api_call"] = datetime(2024, 12, 30, 13, 37, 0).timestamp()

        with patch("flask.session", session_mock) as session:
            with patch("pcapi.core.users.sessions._pro.date_utils") as date_utils_mock:
                date_utils_mock.get_naive_utc_now.return_value = now

                with patch("pcapi.core.users.sessions._pro.datetime") as datetime_mock:
                    datetime_mock.fromtimestamp.side_effect = datetime.fromtimestamp

                result = _pro.manage_pro_session(user)

            assert len(list(session.keys())) == 2
            assert session["last_login"] == expected_last_login
            assert session["last_api_call"] == expected_last_page

        assert result is user

    def test_expired_session(self):
        user = users_factories.ProFactory()

        now = datetime(2024, 1, 1, 12, 0, 0)
        session_mock = DummySession()
        session_mock["last_login"] = (now - timedelta(days=365)).timestamp()
        session_mock["last_api_call"] = (now - timedelta(days=365)).timestamp()

        with patch("pcapi.core.users.sessions._pro.SessionManager.discard_session") as discard_session:
            with patch("flask.session", session_mock):
                result = _pro.manage_pro_session(user)
                discard_session.assert_called_once()
        assert result is None


class ComputeProSessionValidityTest:
    def test_newly_connected(self):
        last_login = date_utils.get_naive_utc_now()
        last_api_call = date_utils.get_naive_utc_now()

        result = _pro.compute_pro_session_validity(last_login, last_api_call)

        assert result

    def test_connexion_expired_but_still_active(self):
        last_login = date_utils.get_naive_utc_now() - settings.PRO_SESSION_LOGIN_TIMEOUT_IN_DAYS
        last_api_call = date_utils.get_naive_utc_now()

        result = _pro.compute_pro_session_validity(last_login, last_api_call)

        assert result

    def test_connexion_expired_and_not_active(self):
        last_login = date_utils.get_naive_utc_now() - settings.PRO_SESSION_LOGIN_TIMEOUT_IN_DAYS
        last_api_call = date_utils.get_naive_utc_now() - (settings.PRO_SESSION_GRACE_TIME_IN_HOURS + timedelta(hours=1))

        result = _pro.compute_pro_session_validity(last_login, last_api_call)

        assert not result

    def test_connexion_expired_but_still_active_older_than_grace_time(self):
        last_login = date_utils.get_naive_utc_now() - settings.PRO_SESSION_FORCE_TIMEOUT_IN_DAYS
        last_api_call = date_utils.get_naive_utc_now()

        result = _pro.compute_pro_session_validity(last_login, last_api_call)

        assert not result
