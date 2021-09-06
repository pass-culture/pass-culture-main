import pytest

import pcapi.core.offerers.factories as offerer_factories


pytestmark = pytest.mark.usefixtures("db_session")


class VenuesTest:
    def test_get_venue(self, client):
        venue = offerer_factories.VenueFactory()

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
            "venueTypeCode": venue.venueTypeCode.value,
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
        }

    def test_get_non_existing_venue(self, client):
        response = client.get("/native/v1/venue/123456789")
        assert response.status_code == 404
