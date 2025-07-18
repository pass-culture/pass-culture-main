from typing import Any

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import VenueTypeCode


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_get_venue_by_id(self, client: Any) -> None:
        venue = offerers_factories.CollectiveVenueFactory(
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
        )

        client.with_eac_token()
        response = client.get(f"/adage/v1/venues/id/{venue.id}")

        assert response.status_code == 200
        venue_address = venue.offererAddress.address
        assert response.json == {
            "id": venue.id,
            "adageId": venue.adageId,
            "name": venue.name,
            "address": venue_address.street,
            "latitude": float(venue_address.latitude),
            "longitude": float(venue_address.longitude),
            "city": venue_address.city,
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
            "siren": venue.managingOfferer.siren,
            "isPermanent": venue.isPermanent,
            "offerer": {"id": venue.managingOfferer.id, "name": venue.managingOfferer.name},
            "bannerUrl": "http://example.com/image_cropped.png",
            "bannerMeta": {
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
        }

    def test_get_relative_venues_by_id(self, client: Any) -> None:
        offerer = offerers_factories.OffererFactory()
        venue1 = offerers_factories.CollectiveVenueFactory(
            isPermanent=True,
            managingOfferer=offerer,
            name="azerty",
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
        )
        venue2 = offerers_factories.CollectiveVenueFactory(
            isPermanent=False,
            managingOfferer=offerer,
            name="zertyu",
            venueTypeCode=VenueTypeCode.OTHER,
        )
        offerers_factories.CollectiveVenueFactory(
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get(f"/adage/v1/venues/relative/id/{venue1.id}")

        assert response.status_code == 200
        venue1_address = venue1.offererAddress.address
        venue2_address = venue2.offererAddress.address
        assert response.json == {
            "venues": [
                {
                    "id": venue1.id,
                    "adageId": venue1.adageId,
                    "name": venue1.name,
                    "address": venue1_address.street,
                    "latitude": float(venue1_address.latitude),
                    "longitude": float(venue1_address.longitude),
                    "city": venue1_address.city,
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
                    "siren": venue1.managingOfferer.siren,
                    "offerer": {"id": venue1.managingOfferer.id, "name": venue1.managingOfferer.name},
                    "bannerUrl": "http://example.com/image_cropped.png",
                    "bannerMeta": {
                        "image_credit": "test",
                        "random": "content",
                        "should": "be_ignored",
                    },
                },
                {
                    "id": venue2.id,
                    "adageId": venue2.adageId,
                    "name": venue2.name,
                    "address": venue2_address.street,
                    "latitude": float(venue2_address.latitude),
                    "longitude": float(venue2_address.longitude),
                    "city": venue2_address.city,
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
                    "siren": venue2.managingOfferer.siren,
                    "offerer": {"id": venue2.managingOfferer.id, "name": venue2.managingOfferer.name},
                    "bannerUrl": None,
                    "bannerMeta": None,
                },
            ]
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client: Any) -> None:
        client.with_eac_token()
        response = client.get("/adage/v1/venues/id/0")

        assert response.status_code == 404
        assert response.json == {"code": "VENUE_NOT_FOUND"}
