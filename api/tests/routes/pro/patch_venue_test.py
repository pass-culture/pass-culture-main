from decimal import Decimal
from unittest.mock import patch

import pytest

from pcapi.core.external.zendesk_sell_backends import testing as zendesk_testing
from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography import models as geography_models
from pcapi.core.history import models as history_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import override_features
from pcapi.core.users import testing as external_testing
from pcapi.utils.date import timespan_str_to_numrange

from tests.routes.pro.post_venue_test import venue_malformed_test_data


pytestmark = pytest.mark.usefixtures("db_session")


def populate_missing_data_from_venue(venue_data: dict, venue: offerers_models.Venue) -> dict:
    return {
        "street": venue.street,
        "banId": venue.banId,
        "bookingEmail": venue.bookingEmail,
        "city": venue.city,
        "latitude": venue.latitude,
        "longitude": venue.longitude,
        "name": venue.name,
        "postalCode": venue.postalCode,
        "publicName": venue.publicName,
        "siret": venue.siret,
        "venueLabelId": venue.venueLabelId,
        "withdrawalDetails": venue.withdrawalDetails,
        "isEmailAppliedOnAllOffers": False,
        "isWithdrawalAppliedOnAllOffers": False,
        "contact": {"email": "no.contact.field@is.mandatory.com"},
        **venue_data,
    }


class Returns200Test:
    def test_should_update_venue(self, client) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(name="old name", managingOfferer=user_offerer.offerer)

        venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "venueTypeCode": "BOOKSTORE",
                "venueLabelId": venue_label.id,
                "withdrawalDetails": "",  # should not appear in history with None => ""
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.filter_by(id=venue_id).one()
        assert venue.publicName == "Ma librairie"
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.BOOKSTORE
        assert response.json["street"] == venue.street
        assert response.json["banId"] == venue.banId
        assert response.json["city"] == venue.city
        assert response.json["siret"] == venue.siret
        assert response.json["postalCode"] == venue.postalCode
        assert len(external_testing.sendinblue_requests) == 1
        assert external_testing.zendesk_sell_requests == [
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            }
        ]

        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].venueId == venue_id
        assert venue.action_history[0].authorUser.id == user_offerer.user.id
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "publicName": {"new_info": "Ma librairie", "old_info": "old name"},
                "venueTypeCode": {
                    "new_info": offerers_models.VenueTypeCode.BOOKSTORE.name,
                    "old_info": offerers_models.VenueTypeCode.OTHER.name,
                },
                "venueLabelId": {"new_info": venue_label.id, "old_info": None},
                "contact.email": {"new_info": "no.contact.field@is.mandatory.com", "old_info": "contact@venue.com"},
                "contact.phone_number": {"new_info": None, "old_info": "+33102030405"},
                "contact.website": {"new_info": None, "old_info": "https://my.website.com"},
            }
        }

    @override_features(ENABLE_API_ADRESSE_WHILE_CREATING_UPDATING_VENUE=True)
    def test_update_venue_location_should_create_offerer_address_if_not_existing(self, client, requests_mock) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, offererAddress=None)

        assert not venue.offererAddress

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        venue_data = populate_missing_data_from_venue(
            {
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.one()
        address = geography_models.Address.query.one()
        offerer_address = offerers_models.OffererAddress.query.one()

        assert venue.offererAddressId == offerer_address.id
        assert address.street == venue.street == "3 Rue de Valois"
        assert address.city == venue.city == "Paris"
        assert address.postalCode == venue.postalCode == "75001"
        assert address.inseeCode.startswith(address.departmentCode)
        assert address.longitude == venue.longitude == Decimal("2.30829")
        assert address.latitude == venue.latitude == Decimal("48.87171")
        assert offerer_address.addressId == address.id
        assert offerer_address.label is None

        assert response.json["street"] == venue.street
        assert response.json["banId"] == venue.banId
        assert response.json["city"] == venue.city
        assert response.json["siret"] == venue.siret
        assert response.json["postalCode"] == venue.postalCode
        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].venueId == venue_id
        assert venue.action_history[0].authorUser.id == user_offerer.user.id
        assert venue.action_history[0].extraData["modified_info"]["street"] == {
            "new_info": "3 Rue de Valois",
            "old_info": "1 boulevard Poissonnière",
        }
        assert venue.action_history[0].extraData["modified_info"]["banId"] == {
            "new_info": "75101_9575_00003",
            "old_info": "75102_7560_00001",
        }
        assert venue.action_history[0].extraData["modified_info"]["latitude"] == {
            "new_info": "48.87171",
            "old_info": "48.87004",
        }
        assert venue.action_history[0].extraData["modified_info"]["longitude"] == {
            "new_info": "2.308289",
            "old_info": "2.3785",
        }
        assert venue.action_history[0].extraData["modified_info"]["postalCode"] == {
            "new_info": "75001",
            "old_info": "75000",
        }

    @override_features(ENABLE_API_ADRESSE_WHILE_CREATING_UPDATING_VENUE=True)
    def test_update_venue_location_should_update_venue_offerer_address(self, client, requests_mock) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        address = geography_factories.AddressFactory(
            street="1 boulevard Poissonnière", postalCode="75000", inseeCode="75000", city="Paris"
        )
        offerer_address = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer, address=address)
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            street=address.street,
            postalCode=address.postalCode,
            city=address.city,
            offererAddress=offerer_address,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        venue_data = populate_missing_data_from_venue(
            {
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.one()
        address = geography_models.Address.query.order_by(geography_models.Address.id.desc()).first()
        offerer_address = offerers_models.OffererAddress.query.one()

        assert venue.offererAddressId == offerer_address.id
        assert address.street == venue.street == "3 Rue de Valois"
        assert address.city == venue.city == "Paris"
        assert address.postalCode == venue.postalCode == "75001"
        assert address.inseeCode.startswith(address.departmentCode)
        assert address.longitude == venue.longitude == Decimal("2.30829")
        assert address.latitude == venue.latitude == Decimal("48.87171")
        assert offerer_address.addressId == address.id
        assert offerer_address.label is None

        assert response.json["street"] == venue.street
        assert response.json["banId"] == venue.banId
        assert response.json["city"] == venue.city
        assert response.json["siret"] == venue.siret
        assert response.json["postalCode"] == venue.postalCode
        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].venueId == venue_id
        assert venue.action_history[0].authorUser.id == user_offerer.user.id
        assert venue.action_history[0].extraData["modified_info"]["street"] == {
            "new_info": "3 Rue de Valois",
            "old_info": "1 boulevard Poissonnière",
        }
        assert venue.action_history[0].extraData["modified_info"]["banId"] == {
            "new_info": "75101_9575_00003",
            "old_info": "75102_7560_00001",
        }
        assert venue.action_history[0].extraData["modified_info"]["latitude"] == {
            "new_info": "48.87171",
            "old_info": "48.87004",
        }
        assert venue.action_history[0].extraData["modified_info"]["longitude"] == {
            "new_info": "2.308289",
            "old_info": "2.3785",
        }
        assert venue.action_history[0].extraData["modified_info"]["postalCode"] == {
            "new_info": "75001",
            "old_info": "75000",
        }

    def test_edit_only_activity_parameters_and_not_venue_accessibility(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )

        venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "venueTypeCode": "BOOKSTORE",
                "venueLabelId": venue_label.id,
                "withdrawalDetails": "",  # should not appear in history with None => ""
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.filter_by(id=venue_id).one()
        assert venue.publicName == "Ma librairie"
        assert venue.audioDisabilityCompliant == None
        assert venue.mentalDisabilityCompliant == None
        assert venue.motorDisabilityCompliant == None
        assert venue.visualDisabilityCompliant == None

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_email_job.delay")
    def test_edit_venue_booking_email_with_applied_on_all_offers(
        self, mocked_update_all_venue_offers_email_job, client
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name", managingOfferer=user_offerer.offerer, bookingEmail="old.venue@email.com"
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "new public name",
                "bookingEmail": "no.update@email.com",
                "isEmailAppliedOnAllOffers": False,
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        assert response.status_code == 200
        assert venue.bookingEmail == "no.update@email.com"
        mocked_update_all_venue_offers_email_job.assert_not_called()

        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "new public name",
                "bookingEmail": "new.venue@email.com",
                "isEmailAppliedOnAllOffers": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

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
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            },
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            },
        ]

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_withdrawal_details_job.delay")
    def test_edit_venue_withdrawal_details_with_applied_on_all_offers(
        self, mocked_update_all_venue_offers_withdrawal_details_job, client
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "new public name",
                "withdrawalDetails": "Ceci est un texte de modalités de retrait",
                "isWithdrawalAppliedOnAllOffers": True,
                "shouldSendMail": True,
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        assert response.status_code == 200
        assert venue.withdrawalDetails == "Ceci est un texte de modalités de retrait"

        mocked_update_all_venue_offers_withdrawal_details_job.assert_called_once_with(
            venue, "Ceci est un texte de modalités de retrait", send_email_notification=True
        )

        assert len(external_testing.sendinblue_requests) == 1
        assert len(external_testing.zendesk_sell_requests) == 1

        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        modified_info = venue.action_history[0].extraData["modified_info"]
        assert modified_info["publicName"] == {"new_info": venue_data["publicName"], "old_info": "old name"}
        assert modified_info["withdrawalDetails"] == {"new_info": venue_data["withdrawalDetails"], "old_info": None}

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_withdrawal_details_job.delay")
    def test_edit_venue_withdrawal_details_with_no_email_notif(
        self, mocked_update_all_venue_offers_withdrawal_details_job, client
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "new public name",
                "withdrawalDetails": "Ceci est un texte de modalités de retrait",
                "isWithdrawalAppliedOnAllOffers": True,
                "shouldSendMail": False,
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        assert response.status_code == 200
        assert venue.withdrawalDetails == "Ceci est un texte de modalités de retrait"

        mocked_update_all_venue_offers_withdrawal_details_job.assert_called_once_with(
            venue, "Ceci est un texte de modalités de retrait", send_email_notification=False
        )

    @patch("pcapi.routes.pro.venues.update_all_venue_offers_accessibility_job.delay")
    def test_edit_venue_accessibility_with_applied_on_all_offers(
        self, mocked_update_all_venue_offers_accessibility_job, client
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
            contact=None,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "new public name",
                "audioDisabilityCompliant": True,
                "isAccessibilityAppliedOnAllOffers": True,
                "contact": None,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        assert response.status_code == 200
        assert venue.audioDisabilityCompliant is True

        mocked_update_all_venue_offers_accessibility_job.assert_called_once_with(
            venue,
            {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
                "motorDisabilityCompliant": venue.motorDisabilityCompliant,
                "visualDisabilityCompliant": venue.visualDisabilityCompliant,
            },
        )

        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].extraData["modified_info"] == {
            "publicName": {"new_info": venue_data["publicName"], "old_info": "old name"},
            "audioDisabilityCompliant": {"new_info": True, "old_info": False},
        }

    def when_siret_does_not_change(self, client) -> None:
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        venue_data = populate_missing_data_from_venue({}, venue)
        auth_request = client.with_session_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # Then
        assert response.status_code == 200
        assert response.json["siret"] == venue.siret

    def test_should_update_permanent_venue_opening_hours(self, client) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, isPermanent=True)

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        # when
        venue_data = populate_missing_data_from_venue(
            {
                "openingHours": [
                    # We are only changing MONDAY and FRIDAY opening Hours, TUESDAY is already like following
                    {"weekday": "MONDAY", "timespan": [["10:00", "13:00"], ["14:00", "19:30"]]},
                    {"weekday": "TUESDAY", "timespan": [["10:00", "13:00"], ["14:00", "19:30"]]},
                    {"weekday": "FRIDAY", "timespan": None},
                ],
                "contact": None,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200
        assert len(venue.action_history) == 1

        tuesday_opening_hours = response.json["openingHours"].get("TUESDAY")
        assert tuesday_opening_hours[0] == {"open": "10:00", "close": "13:00"}
        assert tuesday_opening_hours[1] == {"open": "14:00", "close": "19:30"}

        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "openingHours.MONDAY.timespan": {
                    "old_info": "14:00-19:30",
                    "new_info": "10:00-13:00, 14:00-19:30",
                },
                "openingHours.FRIDAY.timespan": {
                    "old_info": "10:00-13:00, 14:00-19:30",
                    "new_info": None,
                },
            }
        }

    def test_should_not_update_opening_hours_when_response_is_none(self, client) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, isPermanent=True)
        auth_request = client.with_session_auth(email=user_offerer.user.email)

        # when
        venue_data = populate_missing_data_from_venue({"contact": None}, venue)

        # then
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200
        assert len(venue.action_history) == 0

    def test_should_not_update_opening_hours_with_lower_case_weekday(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            contact=None,
        )
        offerers_factories.OpeningHoursFactory(
            venue=venue,
            weekday=offerers_models.Weekday("TUESDAY"),
            timespan=timespan_str_to_numrange([("10:00", "13:00")]),
        )
        venue_data = populate_missing_data_from_venue(
            {
                "contact": {"website": "https://www.venue.com"},
                # Even if weekday is in lower case, it doesn't modify opening hours and must
                # not appear in history
                "weekday": "tuesday",
                "timespan": [["10:00", "13:00"]],
            },
            venue,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200

        assert venue.action_history[0].extraData == {
            "modified_info": {
                "contact.website": {"new_info": venue.contact.website, "old_info": None},
            }
        }


class Returns400Test:
    @pytest.mark.parametrize("data, key", venue_malformed_test_data)
    def test_update_venue_malformed(self, client, data, key):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )

        client = client.with_session_auth(user_offerer.user.email)
        venue_id = venue.id
        response = client.patch(f"/venues/{venue_id}", json=data)

        assert response.status_code == 400
        assert key in response.json

    def test_raises_if_comment_too_long(self, client) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue(
            {"comment": "No SIRET " * 60},
            venue,
        )
        response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert response.json["comment"] == ["ensure this value has at most 500 characters"]

    def test_raises_if_withdrawal_details_too_long(self, client) -> None:
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue(
            {"withdrawalDetails": "blabla " * 100},
            venue,
        )
        response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert response.json["withdrawalDetails"] == ["ensure this value has at most 500 characters"]

    def test_raises_if_invalid_venue_type_code(self, client) -> None:
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue(
            {"venueTypeCode": "("},
            venue,
        )
        response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert response.json["venueTypeCode"] == ["(: invalide"]

    @patch("pcapi.connectors.entreprise.sirene.siret_is_active", return_value=False)
    def test_with_inactive_siret(self, mocked_siret_is_active, client):
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue({"bookingEmail": "new.email@example.com"}, venue)

        response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert response.json["siret"] == ["SIRET is no longer active"]
