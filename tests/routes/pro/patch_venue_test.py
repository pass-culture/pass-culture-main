from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.models import Venue
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


def populate_missing_data_from_venue(venue_data: dict, venue: offerers_models.Venue) -> dict:
    return {
        "address": venue.address,
        "bookingEmail": venue.bookingEmail,
        "city": venue.city,
        "latitude": venue.latitude,
        "longitude": venue.longitude,
        "name": venue.name,
        "postalCode": venue.postalCode,
        "publicName": venue.publicName,
        "siret": venue.siret,
        "venueTypeId": humanize(venue.venueTypeId),
        "venueLabelId": humanize(venue.venueLabelId),
        "withdrawalDetails": venue.withdrawalDetails,
        "isEmailAppliedOnAllOffers": False,
        "isWithdrawalAppliedOnAllOffers": False,
        **venue_data,
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
    @patch("pcapi.routes.pro.venues.update_all_venue_offers_email_job.delay")
    def test_edit_venue_booking_email_with_applied_on_all_offers(self, mocked_update_all_venue_offers_email_job, app):
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            name="old name", managingOfferer=user_offerer.offerer, bookingEmail="old.venue@email.com"
        )

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "name": "new name",
                "bookingEmail": "no.update@email.com",
                "isEmailAppliedOnAllOffers": False,
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 200
        assert venue.bookingEmail == "no.update@email.com"
        mocked_update_all_venue_offers_email_job.assert_not_called()

        venue_data = populate_missing_data_from_venue(
            {
                "name": "new name",
                "bookingEmail": "new.venue@email.com",
                "isEmailAppliedOnAllOffers": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 200
        assert venue.bookingEmail == "new.venue@email.com"

        mocked_update_all_venue_offers_email_job.assert_called_once_with(venue, "new.venue@email.com")

    @pytest.mark.usefixtures("db_session")
    @override_features(ENABLE_VENUE_WITHDRAWAL_DETAILS=True)
    @patch("pcapi.routes.pro.venues.update_all_venue_offers_withdrawal_details_job.delay")
    def test_edit_venue_withdrawal_details_with_applied_on_all_offers(
        self, mocked_update_all_venue_offers_withdrawal_details_job, app
    ):
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "name": "new name",
                "withdrawalDetails": "Ceci est un texte de modalités de retrait",
                "isWithdrawalAppliedOnAllOffers": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 200
        assert venue.withdrawalDetails == "Ceci est un texte de modalités de retrait"

        mocked_update_all_venue_offers_withdrawal_details_job.assert_called_once_with(
            venue, "Ceci est un texte de modalités de retrait"
        )

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


@pytest.mark.usefixtures("db_session")
def test_update_venue_description_too_long(app, client):
    user_offerer = offers_factories.UserOffererFactory()
    venue = offers_factories.VenueFactory(
        managingOfferer=user_offerer.offerer,
    )

    data = {"description": "a" * 1024}

    client = client.with_auth(user_offerer.user.email)
    venue_id = humanize(venue.id)
    response = client.patch(f"/venues/{venue_id}", json=data)

    assert response.status_code == 400
    assert "description" in response.json
