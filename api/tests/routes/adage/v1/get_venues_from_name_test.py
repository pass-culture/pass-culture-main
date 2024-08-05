import pcapi.core.educational.factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories


class Returns200Test:
    def test_get_venues_from_name(self, client, db_session) -> None:
        venue1 = offerers_factories.VenueWithoutSiretFactory(
            name="a beautiful name",
            publicName=None,
            isPermanent=True,
        )
        venue2 = offerers_factories.VenueFactory(
            publicName="a beautiful name",
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="a beautiful name",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 2
        assert {venue["id"] for venue in response_venues} == {venue1.id, venue2.id}

    def test_get_venues_from_name_case_incensitive(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="a beautifUl name",
            publicName=None,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="a beautiful name",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful%20Name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_serialization(self, client, db_session) -> None:
        domain1 = educational_factories.EducationalDomainFactory()
        domain2 = educational_factories.EducationalDomainFactory()
        venue1 = offerers_factories.VenueWithoutSiretFactory(
            name="a beautiful name",
            collectiveDomains=[domain1, domain2],
            collectiveInterventionArea=["mainland"],
            collectiveNetwork=["1"],
            isPermanent=True,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
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
                    "domains": [{"id": domain1.id, "name": domain1.name}, {"id": domain2.id, "name": domain2.name}],
                    "interventionArea": ["mainland"],
                    "network": ["1"],
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

    def test_get_venues_from_name_with_diacritic_in_name_in_db(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="à ñÅmé wïth ç",
            publicName=None,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="somting completely diffetrent",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a%20name%20with%20c")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_with_diacritic_in_public_name_in_db(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="pouet",
            publicName="à ñÅmé wïth ç",
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="somting completely diffetrent",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a%20name%20with%20c")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_with_diacritic_in_name_in_request(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="a name with c",
            publicName=None,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="somting completely diffetrent",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/%C3%A0%20%C3%B1%C3%85m%C3%A9%20w%C3%AFth%20%C3%A7")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_from_name_with_diacritic_in_name_in_request_and_db(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="à ñÅmé wïth ç",
            publicName=None,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="somting completely diffetrent",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/%C3%A0%20%C3%B1%C3%85m%C3%A9%20w%C3%AFth%20%C3%A7")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_ignore_union_request(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="a-composed-name",
            publicName=None,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="somting completely diffetrent",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a-composed-name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_venues_ignore_union_db(self, client, db_session) -> None:
        venue = offerers_factories.VenueWithoutSiretFactory(
            name="a-composed-name",
            publicName=None,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            name="not the same",
            isPermanent=True,
        )
        offerers_factories.VirtualVenueFactory(
            name="somting completely diffetrent",
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/a%20composed%20name")

        assert response.status_code == 200
        response_venues = response.json["venues"]
        assert len(response_venues) == 1
        assert response_venues[0]["id"] == venue.id

    def test_get_relative_venues_from_name(self, client, db_session) -> None:
        offerer = offerers_factories.OffererFactory()
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, name="azerty", isPermanent=True)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, name="z123", isPermanent=False)
        offerers_factories.VenueFactory(isPermanent=True)

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/azerty?getRelative=true")

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
                    "interventionArea": [],
                    "network": None,
                    "statusId": None,
                    "label": None,
                    "siren": venue1.managingOfferer.siren,
                    "isPermanent": venue1.isPermanent,
                    "isAdmin": False,
                    "offerer": {"id": venue1.managingOfferer.id, "name": venue1.managingOfferer.name},
                    "bannerUrl": None,
                    "bannerMeta": None,
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
                    "interventionArea": [],
                    "network": None,
                    "statusId": None,
                    "label": None,
                    "siren": venue2.managingOfferer.siren,
                    "isPermanent": venue2.isPermanent,
                    "isAdmin": False,
                    "offerer": {"id": venue2.managingOfferer.id, "name": venue2.managingOfferer.name},
                    "bannerUrl": None,
                    "bannerMeta": None,
                },
            ]
        }


class Returns404Test:
    def test_when_no_venue_is_found(self, client, db_session) -> None:
        offerers_factories.VenueFactory(name="not the same")

        client.with_eac_token()
        response = client.get("/adage/v1/venues/name/utiful")

        assert response.status_code == 404
        assert response.json == {"code": "VENUES_NOT_FOUND"}
