from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.users import testing as external_testing
from pcapi.core.users.models import UserRole

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class Returns202Test:
    def expect_offerer_to_be_validated(self, app):
        with freeze_time("2021-06-22 14:48:00") as frozen_time:
            # Given
            user_offerer = offerers_factories.UserOffererFactory(offerer__validationToken="TOKEN")

            # When
            frozen_time.move_to("2021-06-23 11:00:00")
            response = TestClient(app.test_client()).get(f"/validate/offerer/{user_offerer.offerer.validationToken}")

        # Then
        assert response.status_code == 202
        assert response.data.decode("utf8") == "Validation effectuée"
        offerer = Offerer.query.filter_by(id=user_offerer.offerer.id).first()
        assert offerer.isValidated is True
        assert offerer.dateValidated == datetime(2021, 6, 23, 11)

        assert len(external_testing.sendinblue_requests) == 1
        assert len(external_testing.zendesk_sell_requests) == 1

    def expect_offerer_to_be_validated_even_when_user_offerer_has_already_been_activated(self, app):
        # Given
        offerer = offerers_factories.OffererFactory(validationToken="TOKEN")
        user_offerer1 = offerers_factories.UserOffererFactory(offerer=offerer)
        user_offerer2 = offerers_factories.UserOffererFactory(validationToken=None, offerer=offerer)

        # When
        response = TestClient(app.test_client()).get(f"/validate/offerer/{offerer.validationToken}")

        # Then
        assert response.status_code == 202
        assert response.data.decode("utf8") == "Validation effectuée"
        offerer = Offerer.query.filter_by(id=offerer.id).first()
        assert offerer.isValidated is True
        assert user_offerer1.user.roles == [UserRole.PRO]
        assert user_offerer2.user.roles == [UserRole.PRO]

        assert len(external_testing.sendinblue_requests) == 2


class Returns404Test:
    def expect_offerer_not_to_be_validated_with_unknown_token(self, app):
        # When
        response = TestClient(app.test_client()).get("/validate/offerer/123")

        # Then
        assert response.status_code == 404
