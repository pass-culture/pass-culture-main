import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.models import db


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
                "banId": venue.offererAddress.address.banId,
                "city": venue.offererAddress.address.city,
                "departmentCode": venue.offererAddress.address.departmentCode,
                "id": venue.offererAddress.addressId,
                "id_oa": venue.offererAddressId,
                "inseeCode": venue.offererAddress.address.inseeCode,
                "isLinkedToVenue": True,
                "isManualEdition": venue.offererAddress.address.isManualEdition,
                "label": venue.common_name,
                "latitude": float(venue.offererAddress.address.latitude),
                "longitude": float(venue.offererAddress.address.longitude),
                "postalCode": venue.offererAddress.address.postalCode,
                "street": venue.offererAddress.address.street,
            },
            "isCaledonian": False,
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
                "banId": venue_with_accessibility_provider.offererAddress.address.banId,
                "city": venue_with_accessibility_provider.offererAddress.address.city,
                "departmentCode": venue_with_accessibility_provider.offererAddress.address.departmentCode,
                "id": venue_with_accessibility_provider.offererAddress.addressId,
                "id_oa": venue_with_accessibility_provider.offererAddressId,
                "inseeCode": venue_with_accessibility_provider.offererAddress.address.inseeCode,
                "isLinkedToVenue": True,
                "isManualEdition": venue_with_accessibility_provider.offererAddress.address.isManualEdition,
                "label": venue_with_accessibility_provider.common_name,
                "latitude": float(venue_with_accessibility_provider.offererAddress.address.latitude),
                "longitude": float(venue_with_accessibility_provider.offererAddress.address.longitude),
                "postalCode": venue_with_accessibility_provider.offererAddress.address.postalCode,
                "street": venue_with_accessibility_provider.offererAddress.address.street,
            },
            "isCaledonian": False,
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


def test_only_return_non_softdeleted_venues(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)
    soft_deleted_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    # We can't set the isSoftDeleted within the factories. It will crash due to the venue
    # not being found.
    soft_deleted_venue.isSoftDeleted = True
    db.session.add(soft_deleted_venue)
    db.session.flush()

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    num_queries += 1  # select venue_ids with validated offers
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1


def test_is_caledonian(client):
    pro_user = users_factories.ProFactory()
    venue = offerers_factories.CaledonianVenueFactory()
    offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user=pro_user)

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    num_queries += 1  # select venue_ids with validated offers
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1
    assert response.json["venues"][0]["isCaledonian"] is True
