from unittest.mock import patch

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import override_features
from pcapi.core.users import testing as external_testing
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient
from tests.routes.pro.post_venue_test import venue_malformed_test_data


pytestmark = pytest.mark.usefixtures("db_session")


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
        "venueLabelId": humanize(venue.venueLabelId),
        "withdrawalDetails": venue.withdrawalDetails,
        "isEmailAppliedOnAllOffers": False,
        "isWithdrawalAppliedOnAllOffers": False,
        "contact": {"email": "no.contact.field@is.mandatory.com"},
        **venue_data,
    }


class Returns200Test:
    def test_should_update_venue(self, app) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(name="old name", managingOfferer=user_offerer.offerer)

        venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = populate_missing_data_from_venue(
            {
                "name": "Ma librairie",
                "venueTypeCode": "BOOKSTORE",
                "venueLabelId": humanize(venue_label.id),
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.get(venue_id)
        assert venue.name == "Ma librairie"
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.BOOKSTORE
        json = response.json
        assert json["isValidated"] is True
        assert "validationToken" not in json
        assert venue.isValidated
        assert len(external_testing.sendinblue_requests) == 1
        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Venue", "id": venue.id}]

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_email_job.delay")
    def test_edit_venue_booking_email_with_applied_on_all_offers(self, mocked_update_all_venue_offers_email_job, app):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name", managingOfferer=user_offerer.offerer, bookingEmail="old.venue@email.com"
        )

        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)

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

        assert len(external_testing.sendinblue_requests) == 4  # former and new booking email, changed twice
        assert {req.get("email") for req in external_testing.sendinblue_requests} == {
            "old.venue@email.com",
            "no.update@email.com",
            "new.venue@email.com",
        }

        assert external_testing.zendesk_sell_requests == [
            # Patch API called twice
            {"action": "update", "type": "Venue", "id": venue.id},
            {"action": "update", "type": "Venue", "id": venue.id},
        ]

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_withdrawal_details_job.delay")
    def test_edit_venue_withdrawal_details_with_applied_on_all_offers(
        self, mocked_update_all_venue_offers_withdrawal_details_job, app
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )

        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)

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

        assert len(external_testing.sendinblue_requests) == 1
        assert len(external_testing.zendesk_sell_requests) == 1

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_accessibility_job.delay")
    def test_edit_venue_accessibility_with_applied_on_all_offers(
        self, mocked_update_all_venue_offers_accessibility_job, app
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )

        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "name": "new name",
                "audioDisabilityCompliant": True,
                "isAccessibilityAppliedOnAllOffers": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 200
        assert venue.audioDisabilityCompliant == True

        mocked_update_all_venue_offers_accessibility_job.assert_called_once_with(
            venue,
            {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
                "motorDisabilityCompliant": venue.motorDisabilityCompliant,
                "visualDisabilityCompliant": venue.visualDisabilityCompliant,
            },
        )

    def when_siret_does_not_change(self, app) -> None:
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        venue_data = populate_missing_data_from_venue({}, venue)
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        assert response.json["siret"] == venue.siret

    def test_add_business_unit_id(self, app) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            businessUnit=None,
        )

        new_business_unit = finance_factories.BusinessUnitFactory(siret=f"{venue.managingOfferer.siren}11111")
        venue_data = populate_missing_data_from_venue(
            {"businessUnitId": new_business_unit.id},
            venue,
        )
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 200
        assert venue.businessUnit.id == new_business_unit.id

        assert len(external_testing.sendinblue_requests) == 1

    def test_remove_business_unit_id(self, app) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        venue_data = populate_missing_data_from_venue(
            {"businessUnitId": None},
            venue,
        )
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 200
        assert venue.businessUnitId == None

        assert len(external_testing.sendinblue_requests) == 1

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_add_reimbursement_point(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")

        new_reimbursement_point = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        finance_factories.BankInformationFactory(venue=new_reimbursement_point)
        venue_data = populate_missing_data_from_venue(
            {"reimbursementPointId": new_reimbursement_point.id},
            venue,
        )
        response = client.with_session_auth(email=user_offerer.user.email).patch(
            f"/venues/{humanize(venue.id)}", json=venue_data
        )

        assert response.status_code == 200
        assert response.json["reimbursementPointId"] == new_reimbursement_point.id
        assert len(external_testing.sendinblue_requests) == 1

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_remove_reimbursement_point_id(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")
        current_reimbursement_point = offerers_factories.VenueFactory()
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue, reimbursementPoint=current_reimbursement_point
        )

        venue_data = populate_missing_data_from_venue(
            {"reimbursementPointId": None},
            venue,
        )
        response = client.with_session_auth(email=user_offerer.user.email).patch(
            f"/venues/{humanize(venue.id)}", json=venue_data
        )

        assert response.status_code == 200
        assert response.json["reimbursementPointId"] is None
        assert len(external_testing.sendinblue_requests) == 1


class Returns400Test:
    def test_error_add_business_unit_id(self, app) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            businessUnit=None,
        )

        new_business_unit = finance_factories.BusinessUnitFactory()
        venue_data = populate_missing_data_from_venue(
            {"businessUnitId": new_business_unit.id},
            venue,
        )
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        assert response.status_code == 400
        assert response.json["businessUnitId"] == ["Ce point de facturation n'est pas un choix valide pour ce lieu."]

    @pytest.mark.parametrize("data, key", venue_malformed_test_data)
    def test_update_venue_malformed(self, client, data, key):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )

        client = client.with_session_auth(user_offerer.user.email)
        venue_id = humanize(venue.id)
        response = client.patch(f"/venues/{venue_id}", json=data)

        assert response.status_code == 400
        assert key in response.json

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_raises_if_different_offerer(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, pricing_point="self")
        another_offerer = offerers_factories.OffererFactory()
        new_reimbursement_point = offerers_factories.VenueFactory(managingOfferer=another_offerer)
        finance_factories.BankInformationFactory(venue=new_reimbursement_point)

        venue_data = populate_missing_data_from_venue(
            {"reimbursementPointId": new_reimbursement_point.id},
            venue,
        )
        response = client.with_session_auth(email=user_offerer.user.email).patch(
            f"/venues/{humanize(venue.id)}", json=venue_data
        )

        assert response.status_code == 400
        assert response.json["reimbursementPointId"] == [
            f"Le lieu {new_reimbursement_point.name} ne peut pas être utilisé pour les remboursements car il n'appartient pas à la même structure."
        ]
