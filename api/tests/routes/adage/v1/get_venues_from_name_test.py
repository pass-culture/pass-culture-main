from pcapi.core.offerers import factories as offerer_factories


class Returns200Test:
    def test_get_venues_from_name(self, client, db_session) -> None:
        venue1 = offerer_factories.VenueFactory(name="a beautiful name")
        venue2 = offerer_factories.VenueFactory(publicName="a beautiful name")
        offerer_factories.VenueFactory(name="not the same")

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 2
        assert {venue["id"] for venue in response_venues} == {venue1.id, venue2.id}

    def test_get_venues_from_name_serialization(self, client, db_session) -> None:
        venue1 = offerer_factories.VenueFactory(name="a beautiful name")

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20name")

        assert response.status_code == 200
        assert response.json == {
            "venues": [
                {
                    "id": venue1.id,
                    "name": venue1.name,
                    "address": venue1.address,
                    "latitude": float(venue1.latitude),
                    "longitude": float(venue1.longitude),
                    "postalCode": venue1.postalCode,
                    "city": venue1.city,
                    "siret": venue1.siret,
                    "publicName": venue1.publicName,
                    "description": venue1.description,
                }
            ]
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client, db_session) -> None:
        offerer_factories.VenueFactory(name="not the same")

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful")

        assert response.status_code == 404
        assert response.json == {"code": "VENUES_NOT_FOUND"}
