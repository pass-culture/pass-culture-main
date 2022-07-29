import pytest

from pcapi.core.offerers import factories as offerer_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_venues_from_siret(self, client) -> None:
        venue = offerer_factories.VenueFactory(
            siret="12345678912345",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/12345678912345")

        assert response.status_code == 200
        assert response.json == {
            "venues": [
                {
                    "id": venue.id,
                    "adageId": venue.adageId,
                    "name": venue.name,
                    "address": venue.address,
                    "latitude": float(venue.latitude),
                    "longitude": float(venue.longitude),
                    "city": venue.city,
                    "siret": venue.siret,
                    "publicName": venue.publicName,
                    "description": venue.description,
                    "collectiveDescription": venue.collectiveDescription,
                    "phoneNumber": venue.contact.phone_number,
                    "email": venue.contact.email,
                    "website": venue.contact.website,
                    "audioDisabilityCompliant": None,
                    "mentalDisabilityCompliant": None,
                    "motorDisabilityCompliant": None,
                    "visualDisabilityCompliant": None,
                }
            ]
        }

    def test_get_venues_from_siret_with_collective_data(self, client) -> None:
        venue = offerer_factories.VenueFactory(
            siret="12345678912345",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveWebsite="https://my.five.level.domain.tld/page.random",
            collectivePhone="0199007788",
            collectiveEmail="user@my.five.level.domain.tld",
            collectiveDescription="collective description maybe",
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/12345678912345")

        assert response.status_code == 200
        assert response.json == {
            "venues": [
                {
                    "id": venue.id,
                    "adageId": venue.adageId,
                    "name": venue.name,
                    "address": venue.address,
                    "latitude": float(venue.latitude),
                    "longitude": float(venue.longitude),
                    "city": venue.city,
                    "siret": venue.siret,
                    "publicName": venue.publicName,
                    "description": venue.description,
                    "collectiveDescription": venue.collectiveDescription,
                    "phoneNumber": venue.collectivePhone,
                    "email": venue.collectiveEmail,
                    "website": venue.collectiveWebsite,
                    "audioDisabilityCompliant": None,
                    "mentalDisabilityCompliant": None,
                    "motorDisabilityCompliant": None,
                    "visualDisabilityCompliant": None,
                }
            ]
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client) -> None:
        client.with_eac_token()
        response = client.get("/adage/v1/venues/a_fake_siret")

        assert response.status_code == 404
        assert response.json == {"code": "VENUES_NOT_FOUND"}
