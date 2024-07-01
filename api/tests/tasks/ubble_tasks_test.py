import pytest

from pcapi import settings
from pcapi.core.testing import assert_num_queries
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


pytestmark = pytest.mark.usefixtures("db_session")


def test_store_id_pictures_task(client):
    # When
    # select beneficiary
    with assert_num_queries(1):
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/ubble/store_id_pictures",
            json={"identification_id": "some-identifier"},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        # Then
        assert response.status_code == 204
