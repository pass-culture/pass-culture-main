from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.offerers.models import Offerer
import pcapi.core.offers.factories as offers_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class Returns202Test:
    def expect_offerer_to_be_validated(self, app):
        with freeze_time("2021-06-22 14:48:00") as frozen_time:
            # Given
            user_offerer = offers_factories.UserOffererFactory(offerer__validationToken="TOKEN")

            # When
            frozen_time.move_to("2021-06-23 11:00:00")
            response = TestClient(app.test_client()).get(
                f"/validate/offerer/{user_offerer.offerer.validationToken}", headers={"origin": "http://localhost:3000"}
            )

        # Then
        assert response.status_code == 202
        assert response.data.decode("utf8") == "Validation effectuée"
        offerer = Offerer.query.filter_by(id=user_offerer.offerer.id).first()
        assert offerer.isValidated is True
        assert offerer.dateValidated == datetime(2021, 6, 23, 11)


class Returns404Test:
    def expect_offerer_not_to_be_validated_with_unknown_token(self, app):
        # When
        response = TestClient(app.test_client()).get("/validate/offerer/123")

        # Then
        assert response.status_code == 404
