from pcapi.core.offerers import factories as offerer_factories


class Returns200Test:
    def test_get_venues_from_name(self, client, db_session) -> None:
        venue1 = offerer_factories.VenueFactory(
            name="a beautiful name",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        venue2 = offerer_factories.VenueFactory(publicName="a beautiful name")
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="a beautiful name", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 2
        assert {venue["id"] for venue in response_venues} == {venue1.id, venue2.id}

    def test_get_venues_from_name_case_incensitive(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="a beautifUl name",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="a beautiful name", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20Name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_serialization(self, client, db_session) -> None:
        venue1 = offerer_factories.VenueFactory(
            name="a beautiful name",
            siret=None,
            comment="no siret",
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20name")

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
                }
            ]
        }

    def test_get_venues_from_name_with_diacritic_in_name_in_db(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="à ñÅmé wïth ç",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="somting completely diffetrent", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a%20name%20with%20c")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_with_diacritic_in_public_name_in_db(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="pouet",
            siret=None,
            comment="no siret",
            publicName="à ñÅmé wïth ç",
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="somting completely diffetrent", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a%20name%20with%20c")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_with_diacritic_in_name_in_request(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="a name with c",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="somting completely diffetrent", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/%C3%A0%20%C3%B1%C3%85m%C3%A9%20w%C3%AFth%20%C3%A7")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_with_diacritic_in_name_in_request_and_db(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="à ñÅmé wïth ç",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="somting completely diffetrent", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/%C3%A0%20%C3%B1%C3%85m%C3%A9%20w%C3%AFth%20%C3%A7")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_ignore_union_request(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="a-composed-name",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="somting completely diffetrent", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a-composed-name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_ignore_union_db(self, client, db_session) -> None:
        venue = offerer_factories.VenueFactory(
            name="a-composed-name",
            siret=None,
            comment="no siret",
            publicName=None,
        )
        offerer_factories.VenueFactory(name="not the same")
        offerer_factories.VenueFactory(isVirtual=True, name="somting completely diffetrent", siret=None)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a%20composed%20name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id


class Returns404Test:
    def test_when_no_venue_is_found(self, client, db_session) -> None:
        offerer_factories.VenueFactory(name="not the same")

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful")

        assert response.status_code == 404
        assert response.json == {"code": "VENUES_NOT_FOUND"}
