import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models import Venue
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


def populate_missing_data_from_venue(venue_data, venue):
    return {
        "address": venue_data["address"] if "address" in venue_data else venue.address,
        "bookingEmail": venue_data["bookingEmail"] if "bookingEmail" in venue_data else venue.bookingEmail,
        "city": venue_data["city"] if "city" in venue_data else venue.city,
        "latitude": venue_data["latitude"] if "latitude" in venue_data else venue.latitude,
        "longitude": venue_data["longitude"] if "longitude" in venue_data else venue.longitude,
        "name": venue_data["name"] if "name" in venue_data else venue.name,
        "postalCode": venue_data["postalCode"] if "postalCode" in venue_data else venue.postalCode,
        "publicName": venue_data["publicName"] if "publicName" in venue_data else venue.publicName,
        "siret": venue_data["siret"] if "siret" in venue_data else venue.siret,
        "venueTypeId": venue_data["venueTypeId"] if "venueTypeId" in venue_data else humanize(venue.venueTypeId),
        "venueLabelId": venue_data["venueLabelId"] if "venueLabelId" in venue_data else humanize(venue.venueLabelId),
    }


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue(self, app) -> None:
        # given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )

        venue_type = offerers_factories.VenueTypeFactory(label="Musée")
        venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = populate_missing_data_from_venue(
            {
                "name": "Ma librairie",
                "venueTypeId": humanize(venue_type.id),
                "venueLabelId": humanize(venue_label.id),
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

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
        venue_data = populate_missing_data_from_venue({}, venue)
        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        assert response.json["siret"] == venue.siret
