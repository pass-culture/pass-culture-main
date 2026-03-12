import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.testing import assert_num_queries
from pcapi.utils import date as date_utils


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
            "latitude": float(venue.offererAddress.address.latitude),
            "longitude": float(venue.offererAddress.address.longitude),
            "city": venue.offererAddress.address.city,
            "publicName": "Public name",
            "isOpenToPublic": venue.isOpenToPublic,
            "isPermanent": venue.isPermanent,
            "isVirtual": False,
            "withdrawalDetails": venue.withdrawalDetails,
            "address": venue.offererAddress.address.street,
            "street": venue.offererAddress.address.street,
            "postalCode": venue.offererAddress.address.postalCode,
            "timezone": venue.offererAddress.address.timezone,
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


class VenueProAdvicesTest:
    def test_returns_venue_pro_advices(self, client):
        offer = offers_factories.OfferFactory()
        venue_id = offer.venue.id
        pro_advice = offers_factories.ProAdviceFactory(offer=offer)
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices")

        assert response.status_code == 200
        assert response.json == {
            "proAdvices": [
                {
                    "author": "Author",
                    "content": "Content",
                    "offerId": offer.id,
                    "offerName": offer.name,
                    "offerCategoryLabel": offer.subcategory.app_label,
                    "offerThumbUrl": offer.thumbUrl,
                    "publicationDatetime": date_utils.format_into_utc_date(pro_advice.updatedAt),
                }
            ],
            "nbResults": 1,
        }

    def test_returns_empty_list(self, client):
        with assert_num_queries(1):
            response = client.get("/native/v1/venue/99999999/advices")

        assert response.status_code == 200
        assert response.json == {"proAdvices": [], "nbResults": 0}

    def test_advices_are_ordered_by_recency(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _newer_advice = offers_factories.ProAdviceFactory(offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 2))
        _older_advice = offers_factories.ProAdviceFactory(offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 1))
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices")

        assert response.status_code == 200
        first = response.json["proAdvices"][0]
        last = response.json["proAdvices"][1]
        assert first["publicationDatetime"] > last["publicationDatetime"]

    def test_trims_content(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _pro_advice = offers_factories.ProAdviceFactory(offer__venue=venue, content="very long content")
        params = {"maxContentLength": 8}
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices", params=params)

        assert response.status_code == 200
        assert response.json["proAdvices"][0]["content"] == "very…"

    def test_returns_only_one_page(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        offers_factories.ProAdviceFactory.create_batch(size=2, offer__venue=venue)
        params = {"resultsPerPage": 1, "page": 1}
        expected_num_queries = 1  # pro_advices
        expected_num_queries = 2  # pro_advices count
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/advices", params=params)

        assert response.status_code == 200
        assert len(response.json["proAdvices"]) == 1
        assert response.json["nbResults"] == 2

    def test_returns_requested_page(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _newer_advice = offers_factories.ProAdviceFactory(
            offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 2), content="Page 1 content"
        )
        _older_advice = offers_factories.ProAdviceFactory(
            offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 1), content="Page 2 content"
        )
        params = {"resultsPerPage": 1, "page": 2}
        expected_num_queries = 1  # pro_advices
        expected_num_queries = 2  # pro_advices count
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/advices", params=params)

        assert response.status_code == 200
        assert response.json["proAdvices"][0]["content"] == "Page 2 content"
        assert response.json["nbResults"] == 2

    def test_page_cannot_be_lt_1(self, client):
        params = {"page": 0, "resultsPerPage": 1}
        with assert_num_queries(0):
            response = client.get("/native/v1/venue/1/advices", params=params)

        assert response.status_code == 400

    def test_results_per_page_cannot_be_lt_1(self, client):
        params = {"page": 1, "resultsPerPage": 0}
        with assert_num_queries(0):
            response = client.get("/native/v1/venue/1/advices", params=params)

        assert response.status_code == 400
