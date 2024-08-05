import pytest

import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_venues_from_siret(self, client) -> None:
        venue = offerers_factories.VenueFactory(
            siret="12345678912345",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveStudents=None,
            collectiveDomains=[],
            collectiveInterventionArea=None,
            collectiveNetwork=None,
            isPermanent=True,
            managingOfferer__siren="12345",
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
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
                    "domains": [],
                    "interventionArea": [],
                    "network": None,
                    "statusId": None,
                    "label": None,
                    "siren": "12345",
                    "isPermanent": venue.isPermanent,
                    "isAdmin": False,
                    "offerer": {"id": venue.managingOfferer.id, "name": venue.managingOfferer.name},
                    "bannerUrl": "http://example.com/image_cropped.png",
                    "bannerMeta": {
                        "image_credit": "test",
                        "random": "content",
                        "should": "be_ignored",
                    },
                }
            ]
        }

    def test_get_venues_from_siret_with_label(self, client) -> None:
        venue = offerers_factories.VenueFactory(
            siret="12345678912345",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveStudents=None,
            collectiveDomains=[],
            collectiveInterventionArea=None,
            collectiveNetwork=None,
            venueLabel=offerers_factories.VenueLabelFactory(),
            isPermanent=True,
            managingOfferer__siren="12345",
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
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
                    "domains": [],
                    "interventionArea": [],
                    "network": None,
                    "statusId": None,
                    "label": {
                        "name": venue.venueLabel.name,
                        "id": venue.venueLabel.id,
                    },
                    "siren": "12345",
                    "isPermanent": venue.isPermanent,
                    "isAdmin": False,
                    "offerer": {"id": venue.managingOfferer.id, "name": venue.managingOfferer.name},
                    "bannerUrl": "http://example.com/image_cropped.png",
                    "bannerMeta": {
                        "image_credit": "test",
                        "random": "content",
                        "should": "be_ignored",
                    },
                }
            ]
        }

    def test_get_venues_from_siret_with_collective_data(self, client) -> None:
        domain1 = educational_factories.EducationalDomainFactory()
        domain2 = educational_factories.EducationalDomainFactory()
        venue = offerers_factories.VenueFactory(
            siret="12345678912345",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveWebsite="https://my.five.level.domain.tld/page.random",
            collectivePhone="0199007788",
            collectiveEmail="user@my.five.level.domain.tld",
            collectiveDescription="collective description maybe",
            collectiveStudents=[StudentLevels.CAP1, StudentLevels.CAP2],
            collectiveDomains=[domain1, domain2],
            collectiveInterventionArea=["75", "92", "971"],
            collectiveNetwork=["1"],
            isPermanent=True,
            managingOfferer__siren="12345",
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
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
                    "domains": [{"id": domain1.id, "name": domain1.name}, {"id": domain2.id, "name": domain2.name}],
                    "interventionArea": ["075", "092", "971"],
                    "network": ["1"],
                    "statusId": None,
                    "label": None,
                    "siren": "12345",
                    "isPermanent": venue.isPermanent,
                    "isAdmin": False,
                    "offerer": {"id": venue.managingOfferer.id, "name": venue.managingOfferer.name},
                    "bannerUrl": "http://example.com/image_cropped.png",
                    "bannerMeta": {
                        "image_credit": "test",
                        "random": "content",
                        "should": "be_ignored",
                    },
                }
            ]
        }

    def test_get_relative_venues_from_siret(self, client) -> None:
        offerer = offerers_factories.OffererFactory()
        venue1 = offerers_factories.VenueFactory(
            siret="12345678912345",
            name="name1",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveStudents=None,
            collectiveDomains=[],
            collectiveInterventionArea=None,
            collectiveNetwork=None,
            managingOfferer=offerer,
            isPermanent=False,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
        )
        venue2 = offerers_factories.VenueFactory(
            siret="9874563211235",
            name="name2",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveStudents=None,
            collectiveDomains=[],
            collectiveInterventionArea=None,
            collectiveNetwork=None,
            managingOfferer=offerer,
            isPermanent=True,
        )
        offerers_factories.VenueFactory(
            siret="7896541238521",
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            collectiveStudents=None,
            collectiveDomains=[],
            collectiveInterventionArea=None,
            collectiveNetwork=None,
            isPermanent=True,
        )

        client.with_eac_token()
        response = client.get("/adage/v1/venues/12345678912345?getRelative=true")

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
                    "audioDisabilityCompliant": None,
                    "mentalDisabilityCompliant": None,
                    "motorDisabilityCompliant": None,
                    "visualDisabilityCompliant": None,
                    "domains": [],
                    "interventionArea": [],
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
                    "audioDisabilityCompliant": None,
                    "mentalDisabilityCompliant": None,
                    "motorDisabilityCompliant": None,
                    "visualDisabilityCompliant": None,
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


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_when_no_venue_is_found(self, client) -> None:
        client.with_eac_token()
        response = client.get("/adage/v1/venues/a_fake_siret")

        assert response.status_code == 404
        assert response.json == {"code": "VENUES_NOT_FOUND"}
