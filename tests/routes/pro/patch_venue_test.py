import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.models import Venue
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200:
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue(self, app) -> None:
        # given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )

        venue_type = offers_factories.VenueTypeFactory(label="Musée")
        venue_label = offers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        response = auth_request.patch(
            "/venues/%s" % humanize(venue.id),
            json={
                "name": "Ma librairie",
                "venueTypeId": humanize(venue_type.id),
                "venueLabelId": humanize(venue_label.id),
            },
        )

        # then
        assert response.status_code == 200
        venue = Venue.query.get(venue_id)
        assert venue.name == "Ma librairie"
        assert venue.venueTypeId == venue_type.id
        json = response.json
        assert json["isValidated"] is True
        assert "validationToken" not in json
        assert venue.isValidated

    @pytest.mark.usefixtures("db_session")
    def when_siret_does_not_change(self, app) -> None:
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        venue_data = {
            "siret": venue.siret,
        }
        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        assert response.json["siret"] == venue.siret
