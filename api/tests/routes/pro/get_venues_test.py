import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.offers.factories import OfferFactory


pytestmark = pytest.mark.usefixtures("db_session")


def test_response_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    venue_with_accessibility_provider = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offerers_factories.AccessibilityProviderFactory(venue=venue_with_accessibility_provider)

    client = client.with_session_auth(user_offerer.user.email)

    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    num_queries += 1  # select venue_ids with validated offers
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 2

    assert response.json["venues"] == [
        {
            "id": venue.id,
            "managingOffererId": venue.managingOffererId,
            "name": venue.name,
            "offererName": user_offerer.offerer.name,
            "publicName": venue.publicName,
            "isVirtual": venue.isVirtual,
            "isPermanent": venue.isPermanent,
            "bookingEmail": venue.bookingEmail,
            "withdrawalDetails": venue.withdrawalDetails,
            "audioDisabilityCompliant": venue.audioDisabilityCompliant,
            "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
            "motorDisabilityCompliant": venue.motorDisabilityCompliant,
            "visualDisabilityCompliant": venue.visualDisabilityCompliant,
            "siret": venue.siret,
            "venueTypeCode": venue.venueTypeCode.name,
            "hasCreatedOffer": False,
            "externalAccessibilityData": None,
            "address": {
                "banId": "75102_7560_00001",
                "city": "Paris",
                "departmentCode": "75",
                "id": venue.offererAddress.addressId,
                "id_oa": venue.offererAddressId,
                "inseeCode": "75102",
                "isLinkedToVenue": True,
                "isManualEdition": False,
                "label": venue.common_name,
                "latitude": 48.87004,
                "longitude": 2.3785,
                "postalCode": "75002",
                "street": "1 boulevard Poissonnière",
            },
        },
        {
            "id": venue_with_accessibility_provider.id,
            "managingOffererId": venue_with_accessibility_provider.managingOffererId,
            "name": venue_with_accessibility_provider.name,
            "offererName": user_offerer.offerer.name,
            "publicName": venue_with_accessibility_provider.publicName,
            "isVirtual": venue_with_accessibility_provider.isVirtual,
            "isPermanent": venue_with_accessibility_provider.isPermanent,
            "bookingEmail": venue_with_accessibility_provider.bookingEmail,
            "withdrawalDetails": venue_with_accessibility_provider.withdrawalDetails,
            "audioDisabilityCompliant": venue_with_accessibility_provider.audioDisabilityCompliant,
            "mentalDisabilityCompliant": venue_with_accessibility_provider.mentalDisabilityCompliant,
            "motorDisabilityCompliant": venue_with_accessibility_provider.motorDisabilityCompliant,
            "visualDisabilityCompliant": venue_with_accessibility_provider.visualDisabilityCompliant,
            "siret": venue_with_accessibility_provider.siret,
            "venueTypeCode": venue_with_accessibility_provider.venueTypeCode.name,
            "hasCreatedOffer": False,
            "externalAccessibilityData": {
                "isAccessibleMotorDisability": True,
                "isAccessibleAudioDisability": True,
                "isAccessibleVisualDisability": True,
                "isAccessibleMentalDisability": False,
                "motorDisability": {
                    "facilities": acceslibre_enum.FACILITIES_UNADAPTED.value,
                    "exterior": acceslibre_enum.EXTERIOR_ACCESS_ELEVATOR.value,
                    "entrance": acceslibre_enum.ENTRANCE_ELEVATOR.value,
                    "parking": acceslibre_enum.PARKING_NEARBY.value,
                },
                "audioDisability": {
                    "deafAndHardOfHearing": [
                        acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value,
                        acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value,
                    ]
                },
                "visualDisability": {
                    "soundBeacon": acceslibre_enum.SOUND_BEACON.value,
                    "audioDescription": [acceslibre_enum.UNKNOWN.value],
                },
                "mentalDisability": {"trainedPersonnel": acceslibre_enum.PERSONNEL_UNTRAINED.value},
            },
            "address": {
                "banId": "75102_7560_00001",
                "city": "Paris",
                "departmentCode": "75",
                "id": venue_with_accessibility_provider.offererAddress.addressId,
                "id_oa": venue_with_accessibility_provider.offererAddressId,
                "inseeCode": "75102",
                "isLinkedToVenue": True,
                "isManualEdition": False,
                "label": venue_with_accessibility_provider.common_name,
                "latitude": 48.87004,
                "longitude": 2.3785,
                "postalCode": "75002",
                "street": "1 boulevard Poissonnière",
            },
        },
    ]


def test_response_created_offer_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()

    venue_with_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, name="venue 1")
    OfferFactory(venue=venue_with_offer)

    venue_with_collective_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, name="venue 2")
    CollectiveOfferFactory(venue=venue_with_collective_offer)

    venue_with_collective_offer_template = offerers_factories.VenueFactory(
        managingOfferer=user_offerer.offerer, name="venue 3"
    )
    CollectiveOfferTemplateFactory(venue=venue_with_collective_offer_template)

    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, name="venue 4")

    client = client.with_session_auth(user_offerer.user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    num_queries += 1  # select venue_ids with validated offers
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 4

    assert response.json["venues"][0]["hasCreatedOffer"] is True
    assert response.json["venues"][1]["hasCreatedOffer"] is True
    assert response.json["venues"][2]["hasCreatedOffer"] is True
    assert response.json["venues"][3]["hasCreatedOffer"] is False


def test_invalid_offerer_id(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)

    params = {"offererId": f"{offerer.id + 1}"}

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues", params)
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 0


def test_full_valid_call(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    params = {
        "validated": "true",
        "offererId": str(offerer.id),
        "activeOfferersOnly": "true",
    }

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues", params)
        assert response.status_code == 200


def test_full_valid_call_with_false(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    params = {
        "validated": "false",
        "offererId": str(offerer.id),
        "activeOfferersOnly": "false",
    }

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues", params)
        assert response.status_code == 200


def test_invalid_validated(client):
    pro_user = users_factories.ProFactory()

    params = {"validated": "invalid"}

    client = client.with_session_auth(pro_user.email)
    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/venues", params)
        assert response.status_code == 400


def test_invalid_active_offerer_only(client):
    pro_user = users_factories.ProFactory()

    params = {"activeOfferersOnly": "invalid"}

    client = client.with_session_auth(pro_user.email)
    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/venues", params)
        assert response.status_code == 400
