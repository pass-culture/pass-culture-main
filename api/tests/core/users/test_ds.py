from unittest.mock import patch

import pytest

from pcapi.connectors.dms.api import GET_INSTRUCTORS_QUERY_NAME
from pcapi.core.users import ds as users_ds
from pcapi.core.users import factories as users_factories


GET_INSTRUCTORS_QUERY_RETURN = {
    "demarche": {
        "groupeInstructeurs": [
            {
                "instructeurs": [
                    {"id": "SW5wdHK1Y3RleRItFDU4MaEs", "email": "one@example.com"},
                    {"id": "SW5wdHK1Y3RleRItMTAvMEI=", "email": "two@example.com"},
                    {"id": "SW5wdHK1Y3RleRItTbAeMpc6", "email": "other_one@example.com"},
                ]
            },
            {"instructeurs": [{"id": "SW5wdHK1Y3RleRItMRAkOCgz", "email": "three@example.com"}]},
        ]
    }
}


@pytest.mark.usefixtures("db_session")
class SyncInstructorIdsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query", return_value=GET_INSTRUCTORS_QUERY_RETURN)
    def test_sync_instructor_ids(self, mocked_get_instructors):
        admin_1 = users_factories.AdminFactory(email="one@example.com", backoffice_profile__dsInstructorId="ABC")
        admin_2 = users_factories.AdminFactory(email="two@example.com")
        admin_3 = users_factories.AdminFactory(email="three@example.com")
        admin_4 = users_factories.AdminFactory(email="four@example.com")

        users_ds.sync_instructor_ids(12345)

        mocked_get_instructors.assert_called_once_with(GET_INSTRUCTORS_QUERY_NAME, variables={"demarcheNumber": 12345})

        assert admin_1.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItFDU4MaEs"
        assert admin_2.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItMTAvMEI="
        assert admin_3.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItMRAkOCgz"
        assert admin_4.backoffice_profile.dsInstructorId is None
