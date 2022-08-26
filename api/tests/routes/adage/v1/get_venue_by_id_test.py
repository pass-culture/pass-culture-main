from typing import Any

import pytest

from pcapi.core.offerers import factories as offerer_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_get_venue_by_id(self, client: Any) -> None:
        venue = offerer_factories.VenueFactory()

        client.with_eac_token()
        response = client.get(f"/adage/v1/venues/id/{venue.id}")

        assert response.status_code == 200
        assert response.json == {
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
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "domains": [],
            "interventionArea": ["75", "92"],
            "network": None,
            "statusId": None,
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client: Any) -> None:
        client.with_eac_token()
        response = client.get("/adage/v1/venues/id/0")

        assert response.status_code == 404
        assert response.json == {"code": "VENUE_NOT_FOUND"}
