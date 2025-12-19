from unittest import mock

import pytest

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @pytest.mark.parametrize(
        "is_only_pro,has_suspended_offerer,is_sole_user_with_ongoing_activities",
        [
            (True, True, False),  # eligible for anonymization
            (False, True, False),  # user has also non pro account
            (True, False, False),  # user has suspended offerer
            (True, True, True),  # user is sole user with ongoing activities
        ],
    )
    @mock.patch("pcapi.routes.pro.users.gdpr_api.is_sole_user_with_ongoing_activities")
    @mock.patch("pcapi.routes.pro.users.gdpr_api.has_suspended_offerer")
    @mock.patch("pcapi.routes.pro.users.gdpr_api.is_only_pro")
    def test_returns_eligibility_status(
        self,
        mock_is_only_pro,
        mock_has_suspended_offerer,
        mock_is_sole_user_with_ongoing_activities,
        client,
        is_only_pro,
        has_suspended_offerer,
        is_sole_user_with_ongoing_activities,
    ):
        user = users_factories.ProFactory()
        mock_is_only_pro.return_value = is_only_pro
        mock_has_suspended_offerer.return_value = has_suspended_offerer
        mock_is_sole_user_with_ongoing_activities.return_value = is_sole_user_with_ongoing_activities

        response = client.with_session_auth(user.email).get("/users/anonymize/eligibility")

        assert response.status_code == 200
        assert response.json == {
            "isOnlyPro": is_only_pro,
            "hasSuspendedOfferer": has_suspended_offerer,
            "isSoleUserWithOngoingActivities": is_sole_user_with_ongoing_activities,
        }
