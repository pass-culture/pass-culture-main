from unittest.mock import patch

import pytest

import pcapi.notifications.push.testing as notifications_testing
from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import factories as dms_factories
from pcapi.core.users import commands as users_commands
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from tests.test_utils import run_command


@pytest.mark.usefixtures("clean_database")
@pytest.mark.features(ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS=True)
@patch(
    "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
    return_value={
        "demarche": {
            "groupeInstructeurs": [
                {"instructeurs": [{"id": "SW5wdHK1Y3RleRItFtH4p6Vs", "email": "instructor@example.com"}]}
            ]
        }
    },
)
def test_sync_instructor_ids(mocked_get_instructors, app):
    user_id = users_factories.AdminFactory(email="instructor@example.com").id

    run_command(app, "sync_ds_instructor_ids")

    mocked_get_instructors.assert_called_once_with(
        dms_api.GET_INSTRUCTORS_QUERY_NAME,
        variables={"demarcheNumber": int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID)},
    )

    # ensure that updated column is really committed
    db.session.close()
    db.session.begin()

    user = db.session.query(users_models.User).filter_by(id=user_id).one()
    assert user.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItFtH4p6Vs"


@pytest.mark.usefixtures("clean_database")
@pytest.mark.features(ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS=True)
@patch(
    "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
    return_value={"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}},
)
def test_sync_ds_user_account_update_requests(mocked_get_applications, app):
    dms_factories.LatestDmsImportFactory(procedureId=settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID)

    run_command(app, "sync_ds_user_account_update_requests")

    mocked_get_applications.assert_called_once()
    assert mocked_get_applications.call_args.args == (dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME,)
    assert mocked_get_applications.call_args.kwargs["variables"]["demarcheNumber"] == int(
        settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID
    )
    assert mocked_get_applications.call_args.kwargs["variables"]["since"] is not None


@pytest.mark.usefixtures("clean_database")
@pytest.mark.features(ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS=True)
@patch(
    "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
    return_value={"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}},
)
def test_sync_ds_user_account_update_requests_ignore_previous(mocked_get_applications, app):
    run_command(app, "sync_ds_user_account_update_requests", "--ignore_previous")

    mocked_get_applications.assert_called_once()
    assert mocked_get_applications.call_args.args == (dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME,)
    assert mocked_get_applications.call_args.kwargs["variables"]["demarcheNumber"] == int(
        settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID
    )
    assert "since" not in mocked_get_applications.call_args.kwargs["variables"]


@pytest.mark.usefixtures("clean_database")
@pytest.mark.features(ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS=False)
@patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query", return_value={})
def test_sync_ds_user_account_update_requests_disabled(mocked_get_applications, app):
    run_command(app, "sync_ds_user_account_update_requests")

    mocked_get_applications.assert_not_called()


@pytest.mark.usefixtures("clean_database")
@pytest.mark.features(ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS=True)
@patch(
    "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
    return_value={"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}},
)
def test_sync_ds_deleted_user_account_update_requests(mocked_get_applications, app):
    run_command(app, "sync_ds_deleted_user_account_update_requests")

    mocked_get_applications.assert_called_once()
    assert mocked_get_applications.call_args.args == (dms_api.GET_DELETED_APPLICATIONS_QUERY_NAME,)
    assert mocked_get_applications.call_args.kwargs["variables"] == {
        "demarcheNumber": int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID)
    }


class SendNotificationFavoritesNotBookedTest:
    def test_send(self):
        rows = [
            {"offer_id": 1, "offer_name": "my offer", "user_ids": [1, 2], "count": 2},
            {"offer_id": 2, "offer_name": "another offer", "user_ids": [3], "count": 1},
        ]

        with patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
            mock_run_query.return_value = rows
            users_commands._send_notification_favorites_not_booked()

        requests = notifications_testing.requests
        assert len(requests) == 2

        user_ids = {*requests[0]["user_ids"], *requests[1]["user_ids"]}
        assert user_ids == {1, 2, 3}

    @pytest.mark.settings(BATCH_MAX_USERS_PER_TRANSACTIONAL_NOTIFICATION=2)
    def test_send_with_split_because_too_many_users(self):
        rows = [
            {"offer_id": 1, "offer_name": "my offer", "user_ids": [1, 2, 3, 4, 5], "count": 5},
        ]

        with patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
            mock_run_query.return_value = rows
            users_commands._send_notification_favorites_not_booked()

        # one request with users 1 and 2
        # another one with users 3 and 4
        # and a final one with user 5
        assert len(notifications_testing.requests) == 3
