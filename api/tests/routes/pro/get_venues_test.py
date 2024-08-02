import pytest

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_response_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    venue_with_accessibility_provider = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offerers_factories.AccessibilityProviderFactory(venue=venue_with_accessibility_provider)

    # when
    client = client.with_session_auth(user_offerer.user.email)
    response = client.get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 2

    assert response.json["venues"] == [
        {
            "id": venue.id,
            "managingOffererId": venue.managingOffererId,
            "collectiveSubCategoryId": venue.collectiveSubCategoryId,
            "name": venue.name,
            "offererName": user_offerer.offerer.name,
            "publicName": venue.publicName,
            "isVirtual": venue.isVirtual,
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
                "id": venue.offererAddressId,
                "inseeCode": "75102",
                "isEditable": False,
                "label": venue.common_name,
                "latitude": 48.87004,
                "longitude": 2.3785,
                "postalCode": "75000",
                "street": "1 boulevard Poissonnière",
            },
        },
        {
            "id": venue_with_accessibility_provider.id,
            "managingOffererId": venue_with_accessibility_provider.managingOffererId,
            "collectiveSubCategoryId": venue_with_accessibility_provider.collectiveSubCategoryId,
            "name": venue_with_accessibility_provider.name,
            "offererName": user_offerer.offerer.name,
            "publicName": venue_with_accessibility_provider.publicName,
            "isVirtual": venue_with_accessibility_provider.isVirtual,
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
                "id": venue_with_accessibility_provider.offererAddressId,
                "inseeCode": "75102",
                "isEditable": False,
                "label": venue_with_accessibility_provider.common_name,
                "latitude": 48.87004,
                "longitude": 2.3785,
                "postalCode": "75000",
                "street": "1 boulevard Poissonnière",
            },
        },
    ]


def test_response_created_offer_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()

    venue_with_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    OfferFactory(venue=venue_with_offer)

    venue_with_collective_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    CollectiveOfferFactory(venue=venue_with_collective_offer)

    venue_with_collective_offer_template = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    CollectiveOfferTemplateFactory(venue=venue_with_collective_offer_template)

    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    client = client.with_session_auth(user_offerer.user.email)
    response = client.get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 4

    assert response.json["venues"][0]["hasCreatedOffer"] is True
    assert response.json["venues"][1]["hasCreatedOffer"] is True
    assert response.json["venues"][2]["hasCreatedOffer"] is True
    assert response.json["venues"][3]["hasCreatedOffer"] is False


def test_admin_call(client):
    admin_user = users_factories.AdminFactory(email="admin.pro@test.com")

    user_offerers = offerers_factories.UserOffererFactory.create_batch(3)

    offerers_factories.VenueFactory(managingOfferer=user_offerers[0].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[1].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[2].offerer)

    # when
    client = client.with_session_auth(admin_user.email)
    with assert_no_duplicated_queries():
        response = client.get("/venues")

    # then
    assert response.status_code == 200
    assert len(response.json["venues"]) == 0


def test_admin_call_with_offerer_id(client):
    admin_user = users_factories.AdminFactory(email="admin.pro@test.com")

    user_offerers = offerers_factories.UserOffererFactory.create_batch(3)

    offerers_factories.VenueFactory(managingOfferer=user_offerers[0].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[1].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[2].offerer)

    # when
    params = {"offererId": str(user_offerers[1].offerer.id)}
    client = client.with_session_auth(admin_user.email)
    # 1 - SELECT user_session
    # 1 - SELECT user
    # 1 - SELECT venue + joined tables
    # 1 - SELECT venue with offers
    with assert_num_queries(4):
        response = client.get("/venues", params)

    # then
    assert response.status_code == 200
    assert len(response.json["venues"]) == 1
    assert response.json["venues"][0]["id"] == user_offerers[1].offerer.managedVenues[0].id


def test_invalid_offerer_id(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)

    params = {"offererId": f"{offerer.id + 1}"}

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
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

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
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

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 200


def test_invalid_validated(client):
    pro_user = users_factories.ProFactory()

    params = {"validated": "invalid"}

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 400


def test_invalid_active_offerer_only(client):
    pro_user = users_factories.ProFactory()

    params = {"activeOfferersOnly": "invalid"}

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 400
