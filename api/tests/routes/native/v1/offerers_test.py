import pytest

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
import pcapi.core.offerers.factories as offerer_factories
from pcapi.core.offerers.models import VenueTypeCode


pytestmark = pytest.mark.usefixtures("db_session")


class VenuesTest:
    def test_get_venue(self, client):
        venue = offerer_factories.VenueFactory(
            isPermanent=True,
            bannerMeta={
                "author_id": 1,
                "original_image_url": "https://ou.ps",
                # only this field should be sent
                "image_credit": "Wikimedia Commons CC By",
            },
        )
        offerer_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="ma-venue",
            externalAccessibilityUrl="https://ra.te",
            externalAccessibilityData={
                "access_modality": [acceslibre_enum.EXTERIOR_ACCESS_ELEVATOR, acceslibre_enum.ENTRANCE_ELEVATOR],
                "audio_description": [
                    acceslibre_enum.AUDIODESCRIPTION_NO_DEVICE,
                    acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL,
                ],
                "deaf_and_hard_of_hearing_amenities": [
                    acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP,
                    acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE,
                ],
                "facilities": [acceslibre_enum.FACILITIES_UNADAPTED],
                "sound_beacon": [],
                "trained_personnel": [acceslibre_enum.PERSONNEL_UNTRAINED],
                "transport_modality": [acceslibre_enum.PARKING_NEARBY],
            },
        )
        response = client.get(f"/native/v1/venue/{venue.id}")

        assert response.status_code == 200
        assert response.json == {
            "id": venue.id,
            "name": venue.name,
            "latitude": float(venue.latitude),
            "longitude": float(venue.longitude),
            "city": venue.city,
            "publicName": venue.publicName,
            "isVirtual": venue.isVirtual,
            "isPermanent": venue.isPermanent,
            "withdrawalDetails": venue.withdrawalDetails,
            "address": venue.street,
            "street": venue.street,
            "postalCode": venue.postalCode,
            "venueTypeCode": "OTHER",
            "description": venue.description,
            "contact": {
                "email": venue.contact.email,
                "phoneNumber": venue.contact.phone_number,
                "website": venue.contact.website,
                "socialMedias": venue.contact.social_medias,
            },
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
                    "deafAndHardOfHearing": f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value}, "
                    f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value}"
                },
                "visualDisability": {
                    "soundBeacon": acceslibre_enum.UNKNOWN.value,
                    "audioDescription": f"{acceslibre_enum.AUDIODESCRIPTION_NO_DEVICE.value}, "
                    f"{acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL.value}",
                },
                "mentalDisability": {"trainedPersonnel": acceslibre_enum.PERSONNEL_UNTRAINED.value},
            },
            "externalAccessibilityId": venue.accessibilityProvider.externalAccessibilityId,
            "externalAccessibilityUrl": venue.accessibilityProvider.externalAccessibilityUrl,
            "accessibility": {
                "audioDisability": venue.audioDisabilityCompliant,
                "mentalDisability": venue.mentalDisabilityCompliant,
                "motorDisability": venue.motorDisabilityCompliant,
                "visualDisability": venue.visualDisabilityCompliant,
            },
            "bannerUrl": venue.bannerUrl,
            "bannerMeta": {
                "image_credit": venue.bannerMeta["image_credit"],
            },
            "openingHours": venue.opening_days,
        }

    def test_get_non_permanent_venue(self, client):
        venue = offerer_factories.VenueFactory(isPermanent=False)
        response = client.get(f"/native/v1/venue/{venue.id}")
        assert response.status_code == 404

    def test_get_non_existing_venue(self, client):
        response = client.get("/native/v1/venue/123456789")
        assert response.status_code == 404

    def test_get_venue_always_has_banner_url(self, client):
        venue = offerer_factories.VenueFactory(venueTypeCode=VenueTypeCode.BOOKSTORE)
        response = client.get(f"/native/v1/venue/{venue.id}")
        assert response.status_code == 200
        assert response.json["bannerUrl"] is not None
