from pcapi.core.offerers import factories as offerer_factories


class Returns200Test:
    def test_get_all_venues_serialization(self, client, db_session) -> None:
        venue1 = offerer_factories.CollectiveVenueFactory(
            name="a beautiful name",
            siret=None,
            comment="no siret",
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
                    "interventionArea": ["75", "92"],
                    "network": None,
                    "statusId": None,
                }
            ]
        }

    def test_get_all_venues_pagination(self, client, db_session) -> None:
        first_venues = offerer_factories.VenueFactory.create_batch(2)
        offerer_factories.VenueFactory(isVirtual=True, siret=None)
        last_venues = offerer_factories.VenueFactory.create_batch(8)

        client.with_eac_token()
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
