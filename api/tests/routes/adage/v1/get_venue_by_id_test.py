from typing import Any

import pytest

from pcapi.core.offerers import factories as offerer_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_get_venue_by_id(self, client: Any) -> None:
        venue = offerer_factories.CollectiveVenueFactory()

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
            "interventionArea": ["075", "092"],
            "network": None,
            "statusId": None,
            "label": None,
            "isPermanent": venue.isPermanent,
        }

    def test_get_relative_venues_by_id(self, client: Any) -> None:
        offerer = offerer_factories.OffererFactory()
        venue1 = offerer_factories.CollectiveVenueFactory(
            isPermanent=True,
            managingOfferer=offerer,
            name="azerty",
        )
        venue2 = offerer_factories.CollectiveVenueFactory(isPermanent=False, managingOfferer=offerer, name="zertyu")
        offerer_factories.CollectiveVenueFactory(
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get(f"/adage/v1/venues/relative/id/{venue1.id}")

        assert response.status_code == 200
        assert response.json == {
            "venues": [
                {
                    "id": venue1.id,
                    "adageId": venue1.adageId,
                    "name": venue1.name,
                    "address": venue1.address,
                    "latitude": float(venue1.latitude),
                    "longitude": float(venue1.longitude),
                    "city": venue1.city,
                    "siret": venue1.siret,
                    "publicName": venue1.publicName,
                    "description": venue1.description,
                    "collectiveDescription": venue1.collectiveDescription,
                    "phoneNumber": venue1.contact.phone_number,
                    "email": venue1.contact.email,
                    "website": venue1.contact.website,
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "domains": [],
                    "interventionArea": ["075", "092"],
                    "network": None,
                    "statusId": None,
                    "label": None,
                    "isPermanent": venue1.isPermanent,
                },
                {
                    "id": venue2.id,
                    "adageId": venue2.adageId,
                    "name": venue2.name,
                    "address": venue2.address,
                    "latitude": float(venue2.latitude),
                    "longitude": float(venue2.longitude),
                    "city": venue2.city,
                    "siret": venue2.siret,
                    "publicName": venue2.publicName,
                    "description": venue2.description,
                    "collectiveDescription": venue2.collectiveDescription,
                    "phoneNumber": venue2.contact.phone_number,
                    "email": venue2.contact.email,
                    "website": venue2.contact.website,
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "domains": [],
                    "interventionArea": ["075", "092"],
                    "network": None,
                    "statusId": None,
                    "label": None,
                    "isPermanent": venue2.isPermanent,
                },
            ]
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client: Any) -> None:
        client.with_eac_token()
        response = client.get("/adage/v1/venues/id/0")

        assert response.status_code == 404
        assert response.json == {"code": "VENUE_NOT_FOUND"}
