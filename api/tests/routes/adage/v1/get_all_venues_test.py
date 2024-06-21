from pcapi.core.offerers import factories as offerer_factories
from pcapi.core.testing import assert_no_duplicated_queries


class Returns200Test:
    def test_get_all_venues_serialization(self, client, db_session) -> None:
        venue1 = offerer_factories.CollectiveVenueFactory(
            name="a beautiful name",
            siret=None,
            comment="no siret",
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues")

        assert response.status_code == 200
        assert response.json == {
            "venues": [
                {
                    "id": venue1.id,
                    "adageId": venue1.adageId,
                    "name": venue1.name,
                    "address": venue1.street,
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
                    "siren": venue1.managingOfferer.siren,
                    "isPermanent": venue1.isPermanent,
                    "isAdmin": False,
                    "offerer": {"id": venue1.managingOfferer.id, "name": venue1.managingOfferer.name},
                    "bannerUrl": "http://example.com/image_cropped.png",
                    "bannerMeta": {
                        "image_credit": "test",
                        "random": "content",
                        "should": "be_ignored",
                    },
                }
            ]
        }

    def test_get_all_venues_pagination(self, client, db_session) -> None:
        first_venues = offerer_factories.VenueFactory.create_batch(2, isPermanent=True)
        offerer_factories.VirtualVenueFactory(isPermanent=True)
        last_venues = offerer_factories.VenueFactory.create_batch(8, isPermanent=True)

        client.with_eac_token()
        with assert_no_duplicated_queries():
            response = client.get("/adage/v1/venues?per_page=2")
        assert response.status_code == 200
        assert len(response.json["venues"]) == 2
        assert {venue["id"] for venue in response.json["venues"]} == {first_venues[0].id, first_venues[1].id}

        response = client.get("/adage/v1/venues?per_page=2&page=2")
        assert response.status_code == 200
        assert len(response.json["venues"]) == 2
        assert {venue["id"] for venue in response.json["venues"]} == {last_venues[0].id, last_venues[1].id}

        response = client.get("/adage/v1/venues")
        assert response.status_code == 200
        assert {venue["id"] for venue in response.json["venues"]} == {venue.id for venue in first_venues + last_venues}


class Returns400Test:
    def test_non_positive_page_query(self, client):
        client.with_eac_token()
        response = client.get("/adage/v1/venues?page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/venues?page=-1")
        assert response.status_code == 400

    def test_non_positive_per_page_query(self, client):
        client.with_eac_token()
        response = client.get("/adage/v1/venues?per_page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/venues?per_page=-1")
        assert response.status_code == 400
