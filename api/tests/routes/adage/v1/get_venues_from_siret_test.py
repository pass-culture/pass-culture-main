import pytest

from pcapi.core.offerers import factories as offerer_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_venues_from_siret(self, client) -> None:
        venue = offerer_factories.VenueFactory(siret="12345678912345")

        client.with_eac_token()
        response = client.get("/adage/v1/venues/12345678912345")

        assert response.status_code == 200
        assert response.json == {
            "venues": [
                {
                    "id": venue.id,
                    "name": venue.name,
                    "address": venue.address,
                    "latitude": float(venue.latitude),
                    "longitude": float(venue.longitude),
                    "city": venue.city,
                    "siret": venue.siret,
                    "publicName": venue.publicName,
                    "description": venue.description,
                }
            ]
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client) -> None:
        client.with_eac_token()
        response = client.get("/adage/v1/venues/a_fake_siret")

        assert response.status_code == 404
        assert response.json == {"code": "VENUES_NOT_FOUND"}
