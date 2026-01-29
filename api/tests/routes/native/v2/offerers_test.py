import pytest

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class GetVenueTest:
    expected_num_queries = 1  # venue with joined tables
    expected_num_queries += 1  # opening hours (selectinload)

    def test_get_venue(self, client):
        venue = offerers_factories.VenueFactory(
            isPermanent=True,
            bannerMeta={
                "author_id": 1,
                "original_image_url": "https://ou.ps",
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
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json == {
            "id": venue.id,
            "accessibilityData": {
                "isAccessibleMotorDisability": venue.audioDisabilityCompliant,
                "isAccessibleAudioDisability": venue.mentalDisabilityCompliant,
                "isAccessibleVisualDisability": venue.motorDisabilityCompliant,
                "isAccessibleMentalDisability": venue.visualDisabilityCompliant,
                "audioDisability": None,
                "mentalDisability": None,
                "motorDisability": None,
                "visualDisability": None,
            },
            "activity": venue.activity.name,
            "bannerCredit": "Wikimedia Commons CC By",
            "bannerIsFromGoogle": False,
            "bannerUrl": venue.bannerUrl,
            "city": venue.offererAddress.address.city,
            "contact": {
                "email": venue.contact.email,
                "phoneNumber": venue.contact.phone_number,
                "website": venue.contact.website,
                "socialMedias": venue.contact.social_medias,
            },
            "description": venue.description,
            "externalAccessibilityData": {
                "isAccessibleMotorDisability": True,
                "isAccessibleAudioDisability": True,
                "isAccessibleVisualDisability": True,
                "isAccessibleMentalDisability": False,
                "audioDisability": {
                    "deafAndHardOfHearing": [
                        acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value,
                        acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value,
                    ]
                },
                "mentalDisability": {"trainedPersonnel": acceslibre_enum.PERSONNEL_UNTRAINED.value},
                "motorDisability": {
                    "facilities": acceslibre_enum.FACILITIES_UNADAPTED.value,
                    "exterior": acceslibre_enum.EXTERIOR_ACCESS_ELEVATOR.value,
                    "entrance": acceslibre_enum.ENTRANCE_ELEVATOR.value,
                    "parking": acceslibre_enum.PARKING_NEARBY.value,
                },
                "visualDisability": {
                    "soundBeacon": acceslibre_enum.UNKNOWN.value,
                    "audioDescription": [
                        acceslibre_enum.AUDIODESCRIPTION_NO_DEVICE.value,
                        acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL.value,
                    ],
                },
            },
            "externalAccessibilityId": venue.accessibilityProvider.externalAccessibilityId,
            "externalAccessibilityUrl": venue.accessibilityProvider.externalAccessibilityUrl,
            "isOpenToPublic": venue.isOpenToPublic,
            "isPermanent": venue.isPermanent,
            "latitude": float(venue.offererAddress.address.latitude),
            "longitude": float(venue.offererAddress.address.longitude),
            "name": "Public name",
            "openingHours": venue.opening_hours,
            "postalCode": venue.offererAddress.address.postalCode,
            "street": venue.offererAddress.address.street,
            "timezone": venue.offererAddress.address.timezone,
            "withdrawalDetails": venue.withdrawalDetails,
        }

    def test_get_venue_google_banner_meta(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.GooglePlacesInfoFactory(
            venue=venue,
            bannerMeta={"html_attributions": ['<a href="http://python.org">Henri</a>']},
        )

        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerCredit"] == "Henri"
        assert response.json["bannerIsFromGoogle"] is True
        assert response.json["bannerUrl"] == venue.bannerUrl

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
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerCredit"] == "Henri"
        assert response.json["bannerIsFromGoogle"] is True
        assert response.json["bannerUrl"] == venue.bannerUrl

    def test_get_venue_google_banner_meta_not_from_google(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True, _bannerMeta={"image_credit": "Henri"})
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerCredit"] == "Henri"
        assert response.json["bannerIsFromGoogle"] is False
        assert response.json["bannerUrl"] == venue.bannerUrl

    def test_get_non_permanent_venue(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=False)
        venue_id = venue.id
        with assert_num_queries(1):  # venue
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 404

    def test_get_venue_closed_offerer(self, client):
        venue = offerers_factories.VenueFactory(
            isPermanent=True, isOpenToPublic=True, managingOfferer=offerers_factories.ClosedOffererFactory()
        )
        venue_id = venue.id
        with assert_num_queries(1):  # venue
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 404

    def test_get_venue_suspended_offerer(self, client):
        venue = offerers_factories.VenueFactory(isPermanent=True, isOpenToPublic=True, managingOfferer__isActive=False)
        venue_id = venue.id
        with assert_num_queries(1):  # venue
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 404

    def test_get_non_existing_venue(self, client):
        with assert_num_queries(1):  # venue
            response = client.get("/native/v1/venue/123456789")
            assert response.status_code == 404

    def test_get_venue_returns_default_banner_url(self, client):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.BOOKSTORE, isPermanent=True)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 200

        assert response.json["bannerUrl"] is not None

    def test_venue_supports_phone_numbers(self, client):
        invalid_phone_number = "+33594282769"  # invalid phone number from real data
        venue = offerers_factories.VenueFactory(contact__phone_number=invalid_phone_number, isPermanent=True)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v2/venue/{venue_id}")
            assert response.status_code == 200

    def test_get_venue_with_no_contact(self, client):
        venue = offerers_factories.VenueFactory(contact=None, isPermanent=True)
        venue_id = venue.id

        response = client.get(f"/native/v2/venue/{venue_id}")
        assert response.status_code == 200
        response_contact = response.json["contact"]
        assert response_contact is None
