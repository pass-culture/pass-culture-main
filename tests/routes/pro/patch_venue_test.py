from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
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
        "withdrawalDetails": venue_data["withdrawalDetails"]
        if "withdrawalDetails" in venue_data
        else venue.withdrawalDetails,
        "isEmailAppliedOnAllOffers": venue_data["isEmailAppliedOnAllOffers"]
        if "isEmailAppliedOnAllOffers" in venue_data
        else False,
        "isWithdrawalAppliedOnAllOffers": venue_data["isWithdrawalAppliedOnAllOffers"]
        if "isWithdrawalAppliedOnAllOffers" in venue_data
        else False,
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
