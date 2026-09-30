import logging
from unittest import mock

import pytest

from pcapi.utils import cloud_sql
from tests.conftest import settings

IAM_SETTINGS = {
    "DATABASE_INSTANCE_CONNECTION_NAME": "my-project:europe-west1:my-instance",
    "DATABASE_DRIVER": "pg8000",
    "DATABASE_IAM_USER": "pcapi-sa@my-project.iam",
    "DATABASE_NAME": "pcapi",
    "DATABASE_IP_TYPE": "private",
}


@pytest.fixture(autouse=True)
def reset_connector():
    cloud_sql._ConnectorHolder.connector = None
    yield
    cloud_sql._ConnectorHolder.connector = None


class GetEngineKwargsTest:
    @pytest.mark.settings(DATABASE_USE_IAM_AUTH="0")
    def test_returns_empty_mapping_without_iam_auth_enabled(self):
        # When
        result = cloud_sql.get_engine_kwargs()

        # Then
        assert cloud_sql.get_engine_kwargs() == {}

    @pytest.mark.settings(DATABASE_USE_IAM_AUTH="1")
    def test_should_returns_iam_creator_when_iam_auth_enabled(self):
        # When
        result = cloud_sql.get_engine_kwargs()

        # then
        assert result == {"creator": cloud_sql.get_iam_connection}


class GetConnectorTest:
    @mock.patch("pcapi.utils.cloud_sql.Connector")
    def test_creates_connector_once(self, connector_class, caplog):
        # When
        with caplog.at_level(logging.INFO):
            first = cloud_sql._get_connector()
            second = cloud_sql._get_connector()

        # Then
        assert first is second
        connector_class.assert_called_once_with(refresh_strategy="lazy")
        assert [record.message for record in caplog.records] == ["Created Cloud SQL connector"]


class GetIamConnectionTest:
    @pytest.mark.settings(**IAM_SETTINGS)
    @mock.patch("pcapi.utils.cloud_sql.Connector")
    def test_connects_with_iam_auth(self, connector_class):
        # When
        connection = cloud_sql.get_iam_connection()

        # Then
        connector = connector_class.return_value
        assert connection is connector.connect.return_value
        connector.connect.assert_called_once_with(
            "my-project:europe-west1:my-instance",
            "pg8000",
            user="pcapi-sa@my-project.iam",
            db="pcapi",
            ip_type="private",
            enable_iam_auth=True,
        )

    @pytest.mark.settings(**IAM_SETTINGS)
    @mock.patch("pcapi.utils.cloud_sql.Connector")
    def test_logs_and_reraises_on_connection_error(self, connector_class, caplog):
        connector_class.return_value.connect.side_effect = RuntimeError("IAM permission denied")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError, match="IAM permission denied"):
                cloud_sql.get_iam_connection()

        record = caplog.records[-1]
        assert record.message == "Could not open IAM connection to Cloud SQL"
        assert record.exc_info is not None
        assert record.instance_connection_name == "my-project:europe-west1:my-instance"
        assert record.iam_user == "pcapi-sa@my-project.iam"
        assert record.database == "pcapi"
        assert record.ip_type == "private"


class DisposeConnectorTest:
    def test_does_nothing_without_connector(self):
        # When
        cloud_sql.dispose_connector()

        # Then
        assert cloud_sql._ConnectorHolder.connector is None

    def test_closes_and_resets_connector(self):
        # Given
        connector = mock.Mock()
        cloud_sql._ConnectorHolder.connector = connector

        # When
        cloud_sql.dispose_connector()

        # Then
        connector.close.assert_called_once_with()
        assert cloud_sql._ConnectorHolder.connector is None

    def test_logs_and_resets_connector_when_close_fails(self, caplog):
        # Given
        connector = mock.Mock()
        connector.close.side_effect = RuntimeError("boom")
        cloud_sql._ConnectorHolder.connector = connector

        # When
        with caplog.at_level(logging.ERROR):
            cloud_sql.dispose_connector()

        # Then
        assert cloud_sql._ConnectorHolder.connector is None
        record = caplog.records[-1]
        assert record.message == "Could not close Cloud SQL connector"
        assert record.exc_info is not None


class ApplySessionTimeoutsTest:
    def test_does_nothing_without_timeouts(self):
        # Given
        dbapi_connection = mock.Mock()

        cloud_sql.apply_session_timeouts(dbapi_connection)

        dbapi_connection.cursor.assert_not_called()

    def test_sets_timeouts_in_autocommit_and_restores_it(self):
        dbapi_connection = mock.Mock(autocommit=False)
        cursor = dbapi_connection.cursor.return_value
        autocommit_during_execute = []
        cursor.execute.side_effect = lambda _: autocommit_during_execute.append(dbapi_connection.autocommit)

        # When
        cloud_sql.apply_session_timeouts(
            dbapi_connection,
            lock_timeout=1000,
            statement_timeout=2000,
            idle_in_transaction_session_timeout=3000,
        )

        # Then
        assert cursor.execute.call_args_list == [
            mock.call("SET SESSION lock_timeout = 1000"),
            mock.call("SET SESSION statement_timeout = 2000"),
            mock.call("SET SESSION idle_in_transaction_session_timeout = 3000"),
        ]
        assert autocommit_during_execute == [True, True, True]
        assert dbapi_connection.autocommit is False
        cursor.close.assert_called_once_with()

    def test_skips_zero_timeouts(self):
        # Given
        dbapi_connection = mock.Mock(autocommit=False)
        cursor = dbapi_connection.cursor.return_value

        # When
        cloud_sql.apply_session_timeouts(dbapi_connection, statement_timeout=2000)

        # Then
        cursor.execute.assert_called_once_with("SET SESSION statement_timeout = 2000")

    def test_restores_autocommit_and_closes_cursor_on_error(self):
        # Given
        dbapi_connection = mock.Mock(autocommit=False)
        cursor = dbapi_connection.cursor.return_value
        cursor.execute.side_effect = RuntimeError("boom")

        # When
        with pytest.raises(RuntimeError):
            cloud_sql.apply_session_timeouts(dbapi_connection, lock_timeout=1000)

        # Then
        cursor.close.assert_called_once_with()
        assert dbapi_connection.autocommit is False
