import pytest

import pcapi.core.offerers.factories as offerer_factories


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
            "address": venue.address,
            "postalCode": venue.postalCode,
            "venueTypeCode": "OTHER",
            "description": venue.description,
            "contact": {
                "email": venue.contact.email,
                "phoneNumber": venue.contact.phone_number,
                "website": venue.contact.website,
                "socialMedias": venue.contact.social_medias,
            },
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
            "venueOpeningHours": venue.opening_days,
        }

    def test_get_non_permanent_venue(self, client):
        venue = offerer_factories.VenueFactory(isPermanent=False)
        response = client.get(f"/native/v1/venue/{venue.id}")
        assert response.status_code == 404

    def test_get_non_existing_venue(self, client):
        response = client.get("/native/v1/venue/123456789")
        assert response.status_code == 404
