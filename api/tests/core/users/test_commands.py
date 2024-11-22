from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors.dms.api import GET_INSTRUCTORS_QUERY_NAME
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from tests.test_utils import run_command


@pytest.mark.usefixtures("clean_database")
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
        GET_INSTRUCTORS_QUERY_NAME, variables={"demarcheNumber": int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID)}
    )

    # ensure that updated column is really committed
    db.session.close()
    db.session.begin()

    user = users_models.User.query.filter_by(id=user_id).one()
    assert user.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItFtH4p6Vs"
