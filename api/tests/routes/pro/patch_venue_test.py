from decimal import Decimal
from unittest.mock import patch

import pytest

import pcapi.connectors.entreprise.exceptions as entreprise_exceptions
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.connectors import acceslibre as acceslibre_connector
from pcapi.core.external.zendesk_sell_backends import testing as zendesk_testing
from pcapi.core.geography import factories as geography_factories
from pcapi.core.history import models as history_models
from pcapi.core.search.models import IndexationReason
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as external_testing
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.date import timespan_str_to_numrange


pytestmark = pytest.mark.usefixtures("db_session")

venue_malformed_test_data = [
    ({"description": "a" * 1024}, "description"),
    ({"contact": {"email": "not_an_email"}}, "contact.email"),
    ({"contact": {"website": "not_an_url"}}, "contact.website"),
    ({"contact": {"phoneNumber": "not_a_phone_number"}}, "contact.phoneNumber"),
    ({"contact": {"social_medias": {"a": "b"}}}, "contact.socialMedias.__key__"),
    ({"contact": {"social_medias": {"facebook": "not_an_url"}}}, "contact.socialMedias.facebook"),
]


def populate_missing_data_from_venue(venue_data: dict, venue: offerers_models.Venue) -> dict:
    address = venue.offererAddress.address
    return {
        "street": address.street,
        "banId": address.banId,
        "bookingEmail": venue.bookingEmail,
        "city": address.city,
        "name": venue.name,
        "postalCode": address.postalCode,
        "publicName": venue.publicName,
        "siret": venue.siret,
        "venueLabelId": venue.venueLabelId,
        "withdrawalDetails": venue.withdrawalDetails,
        "contact": {"email": "no.contact.field@is.mandatory.com"},
        **venue_data,
    }


class Returns200Test:
    def test_should_update_venue(self, client) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )
        initial_address = geography_factories.AddressFactory(
            street="35 Boulevard de Sébastopol",
            postalCode="75001",
            city="Paris",
            inseeCode="75101",
            latitude=48.860939,
            longitude=2.349337,
            banId="75101_8894_00035",
        )
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
            offererAddress__address=initial_address,
            venueTypeCode=offerers_models.VenueTypeCode.PERFORMING_ARTS,
            activity=offerers_models.Activity.PERFORMANCE_HALL,
        )
        initial_location = venue.offererAddress
        venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")
        cultural_domain = educational_factories.EducationalDomainFactory()
        venue.collectiveDomains = [cultural_domain]

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        # when
        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "venueTypeCode": "BOOKSTORE",
                "venueLabelId": venue_label.id,
                "withdrawalDetails": "",  # should not appear in history with None => ""
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "inseeCode": "75056",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
                "isOpenToPublic": True,
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200

        # the venue should be updated
        assert venue.publicName == "Ma librairie"
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.BOOKSTORE
        assert venue.activity == offerers_models.Activity.BOOKSTORE

        # venue location is updated
        new_location = db.session.query(offerers_models.OffererAddress).one()
        assert new_location == initial_location
        new_address = new_location.address

        assert venue.offererAddress == initial_location
        assert new_location.addressId != initial_address.id
        assert new_location.label is None
        assert new_location.type == offerers_models.LocationType.VENUE_LOCATION
        assert new_location.venue == venue
        assert new_address.street == "3 Rue de Valois"
        assert new_address.city == "Paris"
        assert new_address.postalCode == "75001"
        assert new_address.longitude == Decimal("2.30829")
        assert new_address.latitude == Decimal("48.87171")
        assert new_address.banId == "75101_9575_00003"
        assert new_address.inseeCode == "75056"

        # the response should contain updated info
        assert response.json["siret"] == venue.siret
        assert response.json["location"]["street"] == new_address.street
        assert response.json["location"]["banId"] == new_address.banId
        assert response.json["location"]["city"] == new_address.city
        assert response.json["location"]["postalCode"] == new_address.postalCode

        # an update request should be sent to Zendesk
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

        # two updates should be added to venue history
        assert len(venue.action_history) == 2

        # one action should be added for updated venue & location info
        update_action = [
            action
            for action in venue.action_history
            if action.extraData["modified_info"].get("offererAddress.address.street")
        ][0]
        assert update_action.actionType == history_models.ActionType.INFO_MODIFIED
        assert update_action.venueId == venue.id
        assert update_action.authorUser.id == user_offerer.user.id
        update_snapshot = update_action.extraData["modified_info"]
        assert update_snapshot["publicName"]["new_info"] == venue_data["publicName"]
        assert update_snapshot["venueTypeCode"]["new_info"] == venue_data["venueTypeCode"]
        assert update_snapshot["venueLabelId"]["new_info"] == venue_data["venueLabelId"]
        # offerer address & address fields
        assert update_snapshot["offererAddress.address.street"]["new_info"] == new_address.street
        assert update_snapshot["offererAddress.address.inseeCode"]["new_info"] == new_address.inseeCode
        assert update_snapshot["offererAddress.address.banId"]["new_info"] == new_address.banId
        assert update_snapshot["offererAddress.address.latitude"]["new_info"] == str(new_address.latitude)
        assert update_snapshot["offererAddress.address.longitude"]["new_info"] == str(new_address.longitude)
        assert update_snapshot["offererAddress.addressId"]["new_info"] == new_address.id

        # one action should be added for updated accessibility info
        acceslibre_action = [
            action
            for action in venue.action_history
            if action.extraData["modified_info"].get("accessibilityProvider.externalAccessibilityId")
        ][0]
        assert acceslibre_action.extraData["modified_info"] == {
            "accessibilityProvider.externalAccessibilityId": {
                "new_info": "mon-lieu-chez-acceslibre",
                "old_info": None,
            },
            "accessibilityProvider.externalAccessibilityUrl": {
                "new_info": "https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/",
                "old_info": None,
            },
        }

        # Not providing culturalDomains does not change the venue's collective domains
        assert venue.collectiveDomains == [cultural_domain]

    @pytest.mark.parametrize(
        "isOpenToPublic,initial_domains,target_domains",
        (
            pytest.param(True, [0], [1], id="open to public should update the domain"),
            pytest.param(False, [0], [1], id="closed to public should update the domain"),
            pytest.param(True, [], [0, 1], id="adding two domains with no initial domain"),
            pytest.param(True, [0, 1], [], id="removing the two initial domains"),
        ),
    )
    def test_should_update_venue_with_cultual_domain(
        self, isOpenToPublic, initial_domains, target_domains, client
    ) -> None:
        DOMAINS = [
            "Architecture",
            "Arts du cirque et arts de la rue",
            "Arts numériques",
        ]
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
            isOpenToPublic=isOpenToPublic,
        )

        cultural_domains = []
        for i in range(3):
            cultural_domains.append(educational_factories.EducationalDomainFactory(name=DOMAINS[i]))
            if i in initial_domains:
                venue.collectiveDomains.append(cultural_domains[i])

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "culturalDomains": [cultural_domains[i].name for i in target_domains],
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200

        # the venue should be updated
        assert venue.publicName == "Ma librairie"

        # Not providing culturalDomains does not change the venue's collective domains
        assert set(venue.collectiveDomains) == set([cultural_domains[i] for i in target_domains])

    def test_update_venue_is_open_to_public_should_set_is_permanent_to_true_and_sync_acceslibre(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory(user__lastConnectionDate=date_utils.get_naive_utc_now())
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            isOpenToPublic=False,
            isPermanent=True,
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
            activity=offerers_models.Activity.BOOKSTORE,
        )
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        response = auth_request.patch(f"/venues/{venue_id}", {"isOpenToPublic": True})

        assert response.status_code == 200
        db.session.refresh(venue)

        assert venue.isOpenToPublic is True
        assert venue.isPermanent is True
        assert venue.activity == offerers_models.Activity.BOOKSTORE

        assert venue.accessibilityProvider.externalAccessibilityId == "mon-lieu-chez-acceslibre"
        assert set(venue.accessibilityProvider.externalAccessibilityData["access_modality"]) == set(
            [
                acceslibre_connector.ExpectedFieldsEnum.EXTERIOR_ONE_LEVEL.value,
                acceslibre_connector.ExpectedFieldsEnum.ENTRANCE_ONE_LEVEL.value,
            ]
        )

    def test_update_venue_is_close_to_public_should_not_change_is_permanent_but_delete_sync_acceslibre(
        self, client
    ) -> None:
        user_offerer = offerers_factories.UserOffererFactory(user__lastConnectionDate=date_utils.get_naive_utc_now())
        venue = offerers_factories.VenueFactory(
            venueTypeCode=offerers_models.VenueTypeCode.LIBRARY,
            managingOfferer=user_offerer.offerer,
            isOpenToPublic=True,
            isPermanent=True,
        )
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="mon-slug",
            externalAccessibilityUrl="https://acceslibre.beta.gouv.fr/erps/mon-slug/",
        )
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        response = auth_request.patch(f"/venues/{venue_id}", {"isOpenToPublic": False})

        assert response.status_code == 200
        db.session.refresh(venue)

        assert venue.isOpenToPublic is False
        assert venue.isPermanent is True
        assert not venue.accessibilityProvider

    @patch("pcapi.connectors.api_adresse.get_address")
    def test_updating_venue_location_should_rely_on_address_table_data(self, mocked_get_address, client):
        user_offerer = offerers_factories.UserOffererFactory()
        address = geography_factories.AddressFactory(
            banId="12145_1540_0001",
            street="11 Avenue Jean Jaurès",
            postalCode="12100",
            city="Millau",
            latitude=44.10061,
            longitude=3.07889,
            departmentCode="12",
            inseeCode="12145",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, offererAddress__address=address)

        venue_data = populate_missing_data_from_venue(
            {
                "banId": "09160_0350_00011",
                "city": "Lavelanet",
                "latitude": 42.932433,
                "longitude": 1.847675,
                "postalCode": "09300",
                "street": "11 Rue Jean Jaurès",
                "isManualEdition": False,
            },
            venue,
        )
        client_http = client.with_session_auth(email=user_offerer.user.email)

        response = client_http.patch(f"/venues/{venue.id}", json=venue_data)
        assert response.status_code == 200

        response = client_http.get(f"/venues/{venue.id}")
        assert response.json["location"]["street"] == "11 Rue Jean Jaurès"
        assert response.json["location"]["city"] == "Lavelanet"
        assert response.json["location"]["postalCode"] == "09300"

    def test_update_venue_location_with_manual_edition(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        initial_address = geography_factories.AddressFactory(
            street="1 boulevard Poissonnière", postalCode="75000", inseeCode="75000", city="Paris"
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            offererAddress__address=initial_address,
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
                "isManualEdition": True,
                "isOpenToPublic": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200
        venue = db.session.query(offerers_models.Venue).one()
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        new_address = offerer_address.address
        assert venue.offererAddress == offerer_address
        assert new_address.street == "3 Rue de Valois"
        assert new_address.city == "Paris"
        assert new_address.postalCode == "75001"
        assert new_address.inseeCode.startswith(new_address.departmentCode)
        assert new_address.longitude == Decimal("2.30829")
        assert new_address.latitude == Decimal("48.87171")
        assert new_address.isManualEdition
        assert offerer_address.label is None

        assert response.json["siret"] == venue.siret
        assert response.json["location"]["street"] == new_address.street
        assert response.json["location"]["banId"] == new_address.banId
        assert response.json["location"]["city"] == new_address.city
        assert response.json["location"]["postalCode"] == new_address.postalCode
        assert len(venue.action_history) == 2

        update_action = [
            action
            for action in venue.action_history
            if action.extraData["modified_info"].get("offererAddress.address.street")
        ][0]
        update_snapshot = update_action.extraData["modified_info"]
        assert update_action.actionType == history_models.ActionType.INFO_MODIFIED
        assert update_action.venueId == venue_id
        assert update_action.authorUser.id == user_offerer.user.id
        assert update_snapshot["offererAddress.address.street"] == {
            "new_info": new_address.street,
            "old_info": initial_address.street,
        }
        assert update_snapshot["offererAddress.address.latitude"] == {
            "new_info": str(new_address.latitude),
            "old_info": str(initial_address.latitude),
        }
        assert update_snapshot["offererAddress.address.longitude"] == {
            "new_info": str(new_address.longitude),
            "old_info": str(initial_address.longitude),
        }
        assert update_snapshot["offererAddress.address.postalCode"] == {
            "new_info": new_address.postalCode,
            "old_info": initial_address.postalCode,
        }
        assert update_snapshot["offererAddress.address.inseeCode"] == {
            "new_info": new_address.inseeCode,
            "old_info": initial_address.inseeCode,
        }
        assert update_snapshot["offererAddress.address.isManualEdition"] == {
            "new_info": True,
            "old_info": False,
        }

    def test_updating_venue_metadata_shouldnt_create_offerer_address_unnecessarily(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        address = geography_factories.AddressFactory(
            banId=None, street="2 Rue de Valois", postalCode="75000", city="Paris", latitude=48.87055, longitude=2.34765
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, offererAddress__address=address)

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id
        old_venue_name = venue.name

        venue_data = populate_missing_data_from_venue(
            {
                # Updating venue.offererAddress.address to manually edited address
                "street": "3 Rue de Valois",
                "city": "Paris",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
                "isManualEdition": True,
                "isOpenToPublic": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200
        venue = db.session.query(offerers_models.Venue).one()
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        current_address = offerer_address.address
        assert venue.offererAddress == offerer_address
        assert venue.offererAddress.addressId == current_address.id
        assert venue.offererAddress.label is None
        assert venue.offererAddress.address.street == "3 Rue de Valois"
        assert venue.offererAddress.address.city == "Paris"
        assert venue.offererAddress.address.postalCode == "75001"
        assert venue.offererAddress.address.inseeCode.startswith(current_address.departmentCode)
        assert venue.offererAddress.address.latitude == Decimal("48.87171")
        assert venue.offererAddress.address.longitude == Decimal("2.30829")
        assert venue.offererAddress.address.isManualEdition

        assert response.json["siret"] == venue.siret
        assert response.json["location"]["street"] == current_address.street
        assert response.json["location"]["banId"] == current_address.banId
        assert response.json["location"]["city"] == current_address.city
        assert response.json["location"]["postalCode"] == current_address.postalCode

        assert venue.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert venue.action_history[0].venueId == venue_id
        assert venue.action_history[0].authorUser.id == user_offerer.user.id
        assert venue.action_history[0].extraData["modified_info"]["offererAddress.address.street"] == {
            "new_info": "3 Rue de Valois",
            "old_info": "2 Rue de Valois",
        }
        assert venue.action_history[0].extraData["modified_info"]["offererAddress.address.latitude"] == {
            "new_info": "48.87171",
            "old_info": "48.87055",
        }
        assert venue.action_history[0].extraData["modified_info"]["offererAddress.address.longitude"] == {
            "new_info": "2.30829",
            "old_info": "2.34765",
        }
        assert venue.action_history[0].extraData["modified_info"]["offererAddress.address.postalCode"] == {
            "new_info": "75001",
            "old_info": "75000",
        }

        venue_data = populate_missing_data_from_venue(
            {
                # Then updating anything else that the location
                # We shouldn't unnecessarily create an offererAddress
                "publicName": "New public name",
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200

        venue = db.session.query(offerers_models.Venue).one()
        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        # We should still have the same OffererAddress:
        assert venue.offererAddress == offerer_address
        assert venue.offererAddress.addressId == current_address.id

        assert len(venue.action_history[2].extraData["modified_info"]) == 1
        assert venue.action_history[2].extraData["modified_info"]["publicName"] == {
            "new_info": "New public name",
            "old_info": old_venue_name,
        }

    def test_update_venue_location_with_manual_edition_and_oa(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        address = geography_factories.AddressFactory(
            street="1 boulevard Poissonnière", postalCode="75000", inseeCode="75000", city="Paris"
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, offererAddress__address=address)

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_data = populate_missing_data_from_venue(
            {
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
                "isManualEdition": True,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200

        # Ensures we can edit another time the venue just fine
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200

    def test_should_not_create_oa_when_not_updating_location(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            name="old name",
            managingOfferer=user_offerer.offerer,
        )
        update_data = {"bookingEmail": "fakeemail@fake.com"}
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        auth_request.patch("/venues/%s" % venue.id, json=update_data)

        venue = db.session.query(offerers_models.Venue).one()
        offerer_addresses = (
            db.session.query(offerers_models.OffererAddress).order_by(offerers_models.OffererAddress.id).all()
        )
        assert len(offerer_addresses) == 1

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
                "isOpenToPublic": False,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200
        venue = db.session.get(offerers_models.Venue, venue_id)
        assert venue.publicName == "Ma librairie"
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.BOOKSTORE
        assert venue.activity == offerers_models.Activity.NOT_ASSIGNED
        assert venue.audioDisabilityCompliant == None
        assert venue.mentalDisabilityCompliant == None
        assert venue.motorDisabilityCompliant == None
        assert venue.visualDisabilityCompliant == None

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
            venue.id,
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

    def test_when_siret_does_not_change(self, client) -> None:
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

    def test_should_update_open_to_public_venue_opening_hours(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, isOpenToPublic=True)

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_data = populate_missing_data_from_venue(
            {
                "openingHours": {
                    # We are only changing MONDAY and FRIDAY opening Hours, TUESDAY is already like following
                    "MONDAY": [["10:00", "13:00"], ["14:00", "19:30"]],
                    "TUESDAY": [["10:00", "13:00"], ["14:00", "19:30"]],
                    "FRIDAY": None,
                },
                "contact": None,
            },
            venue,
        )

        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)
        assert response.status_code == 200
        assert len(venue.action_history) == 1

        tuesday_opening_hours = response.json["openingHours"].get("TUESDAY")
        assert tuesday_opening_hours == [["10:00", "13:00"], ["14:00", "19:30"]]

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
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, isOpenToPublic=True)
        auth_request = client.with_session_auth(email=user_offerer.user.email)

        venue_data = populate_missing_data_from_venue({"contact": None}, venue)

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

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_when_changes_on_public_name_algolia_indexing_is_triggered(
        self, mocked_async_index_offers_of_venue_ids, client
    ):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
        )
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        json_data = {"publicName": "my new name"}
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once_with(
            [venue.id],
            reason=IndexationReason.VENUE_UPDATE,
            log_extra={"changes": {"publicName"}},
        )

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_when_changes_on_city_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            offererAddress__address__city="old City",
        )
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        json_data = {"city": "My new city"}
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once_with(
            [venue.id],
            reason=IndexationReason.VENUE_UPDATE,
            log_extra={"changes": {"city"}},
        )

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_when_changes_are_not_on_algolia_fields_it_should_not_trigger_indexing(
        self, mocked_async_index_offers_of_venue_ids, client
    ):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            bookingEmail="old@email.com",
        )
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        json_data = {"bookingEmail": "new@email.com"}
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_when_changes_in_payload_are_same_as_previous_it_should_not_trigger_indexing(
        self, mocked_async_index_offers_of_venue_ids, client
    ):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            offererAddress__address__city="old City",
        )
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        json_data = {"city": "old City"}
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    def test_empty_siret_is_editable(self, app, client) -> None:
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueWithoutSiretFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        json_data = {
            "siret": venue.managingOfferer.siren + "11111",
        }
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=json_data)

        # Then
        assert venue.siret == json_data["siret"]

    @pytest.mark.parametrize(
        "venue_data", [{"siret": "12345678954321", "name": "newName"}, {"siret": None, "comment": "test"}]
    )
    def test_existing_siret_is_editable(self, venue_data, app, client) -> None:
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(siret="12345678900001", managingOfferer__siren="123456789")
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        # Then
        assert venue.siret == venue_data["siret"]
        if venue_data["siret"] is not None:
            assert venue.name == venue_data["name"]

    def test_accessibility_fields_are_updated(self, app, client) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        venue_data = {
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        venue = db.session.get(offerers_models.Venue, venue.id)
        assert venue.audioDisabilityCompliant
        assert venue.mentalDisabilityCompliant
        assert venue.motorDisabilityCompliant is False
        assert venue.visualDisabilityCompliant is False

    def test_no_modifications(self, app, client) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # when
        venue_data = {
            "departementCode": venue.offererAddress.address.departmentCode,
            "city": venue.offererAddress.address.city,
            "motorDisabilityCompliant": venue.motorDisabilityCompliant,
            "contact": {
                "email": venue.contact.email,
                "phone_number": venue.contact.phone_number,
                "social_medias": venue.contact.social_medias,
                "website": venue.contact.website,
            },
        }
        http_client = client.with_session_auth(email=user.email)
        venue_id = venue.id

        response = http_client.patch(f"/venues/{venue_id}", json=venue_data)
        assert response.status_code == 200

        assert db.session.query(history_models.ActionHistory).count() == 0

    @patch("pcapi.connectors.virustotal.request_url_scan")
    def test_update_only_venue_contact(self, mock_request_url_scan, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, contact=None)

        # When
        venue_data = {"contact": {"email": "other.contact@venue.com", "phone_number": "0788888888"}}
        http_client = client.with_session_auth(email=user_offerer.user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        venue = db.session.get(offerers_models.Venue, venue.id)
        assert venue.contact
        assert venue.contact.phone_number == "+33788888888"
        assert venue.contact.email == venue_data["contact"]["email"]
        mock_request_url_scan.assert_not_called()

    @patch("pcapi.connectors.virustotal.request_url_scan")
    def test_update_only_venue_website(self, mock_request_url_scan, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # When
        venue_data = {"contact": {"website": "https://new.website.com"}}
        http_client = client.with_session_auth(email=user_offerer.user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        venue = db.session.get(offerers_models.Venue, venue.id)
        assert venue.contact.website == "https://new.website.com"
        mock_request_url_scan.assert_called_once_with(venue_data["contact"]["website"], skip_if_recent_scan=True)

    def test_no_venue_contact_created_if_no_data(self, app, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, contact=None)

        # When
        venue_data = {"contact": {}}
        http_client = client.with_session_auth(email=user_offerer.user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        assert db.session.query(offerers_models.VenueContact).count() == 0

    @patch("pcapi.connectors.virustotal.request_url_scan")
    def test_no_venue_contact_no_modification(self, mock_request_url_scan, client) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(contact=None)
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        venue_data = {
            "departmentCode": venue.offererAddress.address.departmentCode,
            "city": venue.offererAddress.address.city,
            "contact": {"email": None, "phone_number": None, "social_medias": None, "website": None},
        }
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        # then
        # nothing has changed => nothing to save nor update
        assert db.session.query(history_models.ActionHistory).count() == 0
        mock_request_url_scan.assert_not_called()

    @patch("pcapi.connectors.virustotal.request_url_scan")
    def test_no_venue_contact_add_contact(self, mock_request_url_scan, client) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(contact=None)
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        # When
        venue_data = {
            "departmentCode": venue.offererAddress.address.departmentCode,
            "city": venue.offererAddress.address.city,
            "contact": {
                "email": "added@venue.com",
                "phone_number": None,
                "social_medias": None,
                "website": "https://www.venue.com",
            },
        }
        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        # then
        assert venue.contact
        assert venue.contact.email == venue_data["contact"]["email"]
        assert venue.contact.website == venue_data["contact"]["website"]

        # contact info added => an action should be logged in history
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUserId == user.id
        assert action.venueId == venue.id
        assert action.extraData["modified_info"] == {
            "contact.email": {"new_info": venue_data["contact"]["email"], "old_info": None},
            "contact.website": {"new_info": venue_data["contact"]["website"], "old_info": None},
        }
        mock_request_url_scan.assert_called_once_with(venue_data["contact"]["website"], skip_if_recent_scan=True)

    def test_resync_acceslibre_when_address_changes(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        venue_data = {
            "street": "3 rue de Valois",
        }

        http_client = client.with_session_auth(email=user.email)
        http_client.patch(f"/venues/{venue.id}", json=venue_data)

        db.session.refresh(venue)
        assert venue.accessibilityProvider.externalAccessibilityId == "mon-lieu-chez-acceslibre"
        assert set(venue.accessibilityProvider.externalAccessibilityData["access_modality"]) == set(
            [
                acceslibre_connector.ExpectedFieldsEnum.EXTERIOR_ONE_LEVEL.value,
                acceslibre_connector.ExpectedFieldsEnum.ENTRANCE_ONE_LEVEL.value,
            ]
        )

    @pytest.mark.parametrize("venue_name, venue_publicName", [("toto", "toto"), ("toto", "bebechat")])
    def test_update_venue_empty_public_name(self, client, venue_name, venue_publicName):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, name=venue_name, publicName=venue_publicName
        )
        data = {
            "publicName": None,
        }
        http_client = client.with_session_auth(email=user_offerer.user.email)
        response = http_client.patch(f"/venues/{venue.id}", json=data)
        assert response.status_code == 200
        db.session.refresh(venue)
        assert venue.publicName == venue.name  # empty publicname default to name

    def test_update_venue_empty_booking_email(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        data = {
            "bookingEmail": "",
        }
        http_client = client.with_session_auth(email=user_offerer.user.email)
        response = http_client.patch(f"/venues/{venue.id}", json=data)
        assert response.status_code == 200
        db.session.refresh(venue)
        assert venue.bookingEmail is None

    @pytest.mark.parametrize(
        "isOpenToPublic, venueTypeCode, activity, expected_venueTypeCode, expected_activity",
        [
            (True, "MOVIE", None, offerers_models.VenueTypeCode.MOVIE, offerers_models.Activity.CINEMA),
            (True, None, "CINEMA", offerers_models.VenueTypeCode.MOVIE, offerers_models.Activity.CINEMA),
            (True, "BOOKSTORE", "CINEMA", offerers_models.VenueTypeCode.BOOKSTORE, offerers_models.Activity.CINEMA),
            (False, "MOVIE", None, offerers_models.VenueTypeCode.MOVIE, offerers_models.Activity.NOT_ASSIGNED),
            (
                False,
                None,
                "STREAMING_PLATFORM",
                offerers_models.VenueTypeCode.DIGITAL,
                offerers_models.Activity.STREAMING_PLATFORM,
            ),
            (
                False,
                "BOOKSTORE",
                "STREAMING_PLATFORM",
                offerers_models.VenueTypeCode.BOOKSTORE,
                offerers_models.Activity.STREAMING_PLATFORM,
            ),
            (True, None, "FESTIVAL", offerers_models.VenueTypeCode.FESTIVAL, offerers_models.Activity.FESTIVAL),
            (False, None, "FESTIVAL", offerers_models.VenueTypeCode.FESTIVAL, offerers_models.Activity.FESTIVAL),
        ],
    )
    def test_update_activity_or_venue_type_code(
        self, client, isOpenToPublic, venueTypeCode, activity, expected_venueTypeCode, expected_activity
    ) -> None:
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            venueTypeCode=offerers_models.VenueTypeCode.ARTISTIC_COURSE,
            activity=offerers_models.Activity.ART_SCHOOL,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        # when
        extra_data = {}
        if venueTypeCode:
            extra_data["venueTypeCode"] = venueTypeCode
        if activity:
            extra_data["activity"] = activity
        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "withdrawalDetails": "",  # should not appear in history with None => ""
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "inseeCode": "75056",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
                "isOpenToPublic": isOpenToPublic,
            }
            | extra_data,
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200, response.json

        # the venue should be updated
        assert venue.venueTypeCode == expected_venueTypeCode
        assert venue.activity == expected_activity

    @pytest.mark.parametrize(
        "isOpenToPublic, venueTypeCode, activity, expected_venueTypeCode, expected_activity",
        [
            (True, None, None, offerers_models.VenueTypeCode.GAMES, offerers_models.Activity.GAMES_CENTRE),
            (False, None, None, offerers_models.VenueTypeCode.GAMES, offerers_models.Activity.GAMES_CENTRE),
            (True, "MOVIE", None, offerers_models.VenueTypeCode.MOVIE, offerers_models.Activity.CINEMA),
            (False, "MOVIE", None, offerers_models.VenueTypeCode.MOVIE, offerers_models.Activity.NOT_ASSIGNED),
            (True, None, "CINEMA", offerers_models.VenueTypeCode.MOVIE, offerers_models.Activity.CINEMA),
        ],
    )
    def test_update_game_center_activity_or_venue_type_code(
        self, client, isOpenToPublic, venueTypeCode, activity, expected_venueTypeCode, expected_activity
    ) -> None:
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            venueTypeCode=offerers_models.VenueTypeCode.GAMES,
            activity=offerers_models.Activity.GAMES_CENTRE,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        # when
        extra_data = {}
        if venueTypeCode:
            extra_data["venueTypeCode"] = venueTypeCode
        if activity:
            extra_data["activity"] = activity
        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "withdrawalDetails": "",  # should not appear in history with None => ""
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "inseeCode": "75056",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
                "isOpenToPublic": isOpenToPublic,
            }
            | extra_data,
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 200

        # the venue should be updated
        assert venue.venueTypeCode == expected_venueTypeCode
        assert venue.activity == expected_activity


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

    def test_with_inactive_siret(self, client):
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        # SIRET looking like xxxx99xxxxxxxx is inactive in our testing data
        venue_data = populate_missing_data_from_venue(
            {"bookingEmail": "new.email@example.com", "siret": "12349912345678"}, venue
        )

        response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert response.json["siret"] == ["SIRET is no longer active"]

    @pytest.mark.parametrize("venue_data", [{"name": "New name"}, {"name": None}])
    def test_name_is_not_editable(self, venue_data, app, client) -> None:
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        http_client = client.with_session_auth(email=user.email)

        response = http_client.patch(f"/venues/{venue.id}", json=venue_data)

        # Then
        assert response.status_code == 400
        assert "Vous ne pouvez pas modifier la raison sociale d'un lieu" in response.json["name"]

    def test_remove_siret(self, app, client) -> None:
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            siret="12345678900001",
            managingOfferer__siren="123456789",
        )
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        http_client = client.with_session_auth(email=user.email)

        response = http_client.patch(f"/venues/{venue.id}", json={"siret": None})

        assert response.status_code == 400
        assert response.json["siret"] == ["Vous ne pouvez pas supprimer le siret d'un lieu"]

    def test_edit_with_siret_not_tied_to_siren(self, app, client) -> None:
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            siret="12345678900001",
            managingOfferer__siren="123456789",
        )
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        http_client = client.with_session_auth(email=user.email)

        response = http_client.patch(f"/venues/{venue.id}", json={"siret": "22345678900001"})

        assert response.status_code == 400
        assert response.json["siret"] == ["Le code SIRET doit correspondre à un établissement de votre structure"]

    def test_raises_if_coordinates_are_not_numbers(self, client) -> None:
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue(
            {"latitude": "not a number", "longitude": "not a number either"},
            venue,
        )

        response = client.with_session_auth(email=user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert "La latitude doit être un nombre" in response.json["latitude"]
        assert "La longitude doit être un nombre" in response.json["longitude"]

    def test_raises_if_coordinates_are_out_of_bonds(self, client) -> None:
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue(
            {"latitude": 200, "longitude": -200},
            venue,
        )

        response = client.with_session_auth(email=user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert "La latitude doit être comprise entre -90 et +90" in response.json["latitude"]
        assert "La longitude doit être comprise entre -180 et +180" in response.json["longitude"]

    def test_raise_if_invalid_booking_email(self, client) -> None:
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        venue_data = populate_missing_data_from_venue({"bookingEmail": "invalid-email-format"}, venue)

        response = client.with_session_auth(email=user.email).patch(f"/venues/{venue.id}", json=venue_data)

        assert response.status_code == 400
        assert "Le format d'email est incorrect." in response.json["bookingEmail"]

    def test_update_with_invalid_activity(self, client) -> None:
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            venueTypeCode=offerers_models.VenueTypeCode.GAMES,
            activity=offerers_models.Activity.GAMES_CENTRE,
            isOpenToPublic=True,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        # when
        venue_data = populate_missing_data_from_venue(
            {
                "publicName": "Ma librairie",
                "withdrawalDetails": "",  # should not appear in history with None => ""
                # Default data from api adresse TestingBackend
                "street": "3 Rue de Valois",
                "banId": "75101_9575_00003",
                "city": "Paris",
                "inseeCode": "75056",
                "latitude": 48.87171,
                "longitude": 2.308289,
                "postalCode": "75001",
                "isOpenToPublic": False,
                "activity": offerers_models.Activity.CINEMA.value,
            },
            venue,
        )
        response = auth_request.patch("/venues/%s" % venue.id, json=venue_data)

        # then
        assert response.status_code == 400
        assert response.json == {"activity": ["Activité non reconnue."]}


@pytest.mark.parametrize(
    "enforce_siret_check,disable_siret_check,expected_result",
    [
        (True, False, 400),
        (True, True, 400),
        (False, False, 400),
        (False, True, 200),
    ],
)
@patch(
    "pcapi.connectors.entreprise.api.get_siret_open_data",
    side_effect=entreprise_exceptions.UnknownEntityException(),
)
def test_with_inconsistent_siret(
    mock_get_siret_open_data, client, features, settings, enforce_siret_check, disable_siret_check, expected_result
):
    venue = offerers_factories.VenueFactory(siret="00112233900040", managingOfferer__siren="001122339")
    user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

    venue_data = populate_missing_data_from_venue({"siret": "00112233900049"}, venue)

    settings.ENFORCE_SIRET_CHECK = enforce_siret_check
    features.DISABLE_SIRET_CHECK = disable_siret_check
    response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

    assert response.status_code == expected_result, response.json
    if expected_result == 400:
        assert response.json == {"global": ["Le SIREN n’existe pas."]}


@pytest.mark.parametrize(
    "new_ridet,enforce_siret_check,disable_siret_check,expected_result",
    [
        ("NC1234567000XX", True, False, 200),
        ("NC1234567000XX", True, True, 200),
        ("NC1234567000XX", False, False, 200),
        ("NC1234567000XX", False, True, 200),
        ("NC0234567890XX", False, True, 400),  # nok: ridet does not start with rid7
    ],
)
@patch(
    "pcapi.connectors.entreprise.api.get_siret_open_data",
    side_effect=entreprise_exceptions.UnknownEntityException(),
)
def test_with_new_caledonian_ridet(
    mock_get_siret_open_data,
    client,
    features,
    settings,
    new_ridet,
    enforce_siret_check,
    disable_siret_check,
    expected_result,
):
    venue = offerers_factories.VenueFactory(siret="NC1234567890XX", managingOfferer__siren="NC1234567")
    user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

    venue_data = populate_missing_data_from_venue({"siret": new_ridet}, venue)

    settings.ENFORCE_SIRET_CHECK = enforce_siret_check
    features.DISABLE_SIRET_CHECK = disable_siret_check
    response = client.with_session_auth(email=user_offerer.user.email).patch(f"/venues/{venue.id}", json=venue_data)

    assert response.status_code == expected_result, response.json
    if expected_result == 200:
        assert venue.siret == new_ridet
    if expected_result == 400:
        assert response.json == {"siret": ["Le code RIDET doit correspondre à un établissement de votre structure"]}
