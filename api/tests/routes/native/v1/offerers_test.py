import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core import testing
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class VenuesTest:
    expected_num_queries = 5  # venue + google_places_info + venue_contact + accessibility_provider + opening_hours

    def test_get_venue(self, client):
        venue = offerers_factories.VenueFactory(
            isPermanent=True,
            bannerMeta={
                "author_id": 1,
                "original_image_url": "https://ou.ps",
                # only this field should be sent
                "image_credit": "Wikimedia Commons CC By",
            },
            isOpenToPublic=True,
            name="Legal name",
            publicName="Public name",
        )
        offerers_factories.AccessibilityProviderFactory(
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
        venue_id = venue.id

        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json == {
            "id": venue.id,
            "name": "Public name",
            "latitude": float(venue.latitude),
            "longitude": float(venue.longitude),
            "city": venue.city,
            "publicName": "Public name",
            "isVirtual": venue.isVirtual,
            "isOpenToPublic": venue.isOpenToPublic,
            "isPermanent": venue.isPermanent,
            "withdrawalDetails": venue.withdrawalDetails,
            "address": venue.street,
            "street": venue.street,
            "postalCode": venue.postalCode,
            "timezone": venue.timezone,
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
                    "deafAndHardOfHearing": [
                        acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value,
                        acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value,
                    ]
                },
                "visualDisability": {
                    "soundBeacon": acceslibre_enum.UNKNOWN.value,
                    "audioDescription": [
                        acceslibre_enum.AUDIODESCRIPTION_NO_DEVICE.value,
                        acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL.value,
                    ],
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
            "openingHours": venue.opening_hours,
        }

    def test_get_venue_google_banner_meta(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.GooglePlacesInfoFactory(
            venue=venue,
            bannerMeta={"html_attributions": ['<a href="http://python.org">Henri</a>']},
        )

        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerUrl"] == venue.bannerUrl
        assert response.json["bannerMeta"] == {
            "image_credit": "Henri",
            "image_credit_url": "http://python.org",
            "is_from_google": True,
        }

    def test_get_venue_google_banner_meta_multiple_attributions(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.GooglePlacesInfoFactory(
            venue=venue,
            bannerMeta={
                "html_attributions": [
                    '<a href="http://python.org">Henri</a>',
                    '<a href="http://leblogdufun.fr">Kelly</a>',
                ]
            },
        )

        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerUrl"] == venue.bannerUrl
        assert response.json["bannerMeta"] == {
            "image_credit": "Henri",
            "image_credit_url": "http://python.org",
            "is_from_google": True,
        }

    def test_get_venue_google_banner_meta_not_from_google(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True, _bannerMeta={"image_credit": "Henri"})
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerUrl"] == venue.bannerUrl
        assert response.json["bannerMeta"] == {"image_credit": "Henri"}

    def test_get_non_permanent_venue(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=False)
        venue_id = venue.id
        with assert_num_queries(1):  # venue
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 404

    def test_get_venue_closed_offerer(self, client):
        venue = offerers_factories.VenueFactory(
            isPermanent=True, isOpenToPublic=True, managingOfferer=offerers_factories.ClosedOffererFactory()
        )
        venue_id = venue.id
        with assert_num_queries(1):  # venue
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 404

    def test_get_venue_suspended_offerer(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True, isOpenToPublic=True, managingOfferer__isActive=False)
        venue_id = venue.id
        with assert_num_queries(1):  # venue
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 404

    def test_get_non_existing_venue(self, client):
        with assert_num_queries(1):  # venue
            response = client.get("/native/v1/venue/123456789")
            assert response.status_code == 404

    def test_get_venue_always_has_banner_url(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.BOOKSTORE)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerUrl"] is not None

    def test_venue_supports_phone_numbers(self, client):
        invalid_phone_number = "+33594282769"  # invalid phone number from real data
        venue = offerers_factories.VenueFactory(
            venueTypeCode=VenueTypeCode.BOOKSTORE, contact__phone_number=invalid_phone_number
        )
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}")
            assert response.status_code == 200


class OffererHeadlineOfferTest:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer
    num_queries += 1  # get headline offer

    def test_get_offerer_headline_offer_success(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        headline_offer = offers_factories.HeadlineOfferFactory(offer=offer, venue=venue)

        client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer.id}/headline-offer")

        assert response.status_code == 200
        assert response.json == {
            "name": offer.name,
            "id": offer.id,
            "image": {
                "credit": offer.image.credit,
                "url": offer.image.url,
            },
            "venueId": headline_offer.venueId,
        }

    def test_get_offerer_headline_offer_not_found(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer

        client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.num_queries + 1):  # +1 for atomic rollback
            response = client.get(f"/offerers/{offerer.id}/headline-offer")
            assert response.status_code == 404
