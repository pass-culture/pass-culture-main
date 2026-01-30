import pytest
import time_machine
from flask import url_for

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


def get_test_client(client, redactor, institution):
    if not institution:
        return client.with_adage_token(email=redactor.email, uai=None)
    return client.with_adage_token(email=redactor.email, uai=institution.institutionId)


class GetFavoriteOfferTest:
    endpoint = "adage_iframe.get_collective_favorites"
    num_queries = 1  # fetch redactor
    num_queries += 1  # fetch collective offer template and related data

    @time_machine.travel("2020-11-17 15:00:00")
    def test_get_favorite_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[collective_offer_template],
        )

        test_client = get_test_client(client, educational_redactor, educational_institution)
        with assert_num_queries(self.num_queries):
            response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {
            "favoritesTemplate": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": collective_offer_template.id,
                    "description": collective_offer_template.description,
                    "isFavorite": True,
                    "name": collective_offer_template.name,
                    "venue": {
                        "adageId": None,
                        "address": collective_offer_template.venue.offererAddress.address.street,
                        "city": "Paris",
                        "coordinates": {
                            "latitude": float(collective_offer_template.venue.offererAddress.address.latitude),
                            "longitude": float(collective_offer_template.venue.offererAddress.address.longitude),
                        },
                        "id": collective_offer_template.venue.id,
                        "imgUrl": None,
                        "managingOfferer": {"name": collective_offer_template.venue.managingOfferer.name},
                        "name": collective_offer_template.venue.name,
                        "postalCode": collective_offer_template.venue.offererAddress.address.postalCode,
                        "departmentCode": collective_offer_template.venue.offererAddress.address.departmentCode,
                        "publicName": collective_offer_template.venue.publicName,
                    },
                    "students": ["Lycée - Seconde"],
                    "location": {
                        "location": None,
                        "locationComment": None,
                        "locationType": "TO_BE_DEFINED",
                    },
                    "contactEmail": "collectiveofferfactory+contact@example.com",
                    "contactPhone": collective_offer_template.contactPhone,
                    "contactUrl": collective_offer_template.contactUrl,
                    "contactForm": collective_offer_template.contactForm.value,
                    "durationMinutes": None,
                    "educationalPriceDetail": collective_offer_template.priceDetail,
                    "domains": [
                        {
                            "id": collective_offer_template.domains[0].id,
                            "name": collective_offer_template.domains[0].name,
                        }
                    ],
                    "interventionArea": ["2A", "2B"],
                    "imageUrl": None,
                    "nationalProgram": None,
                    "dates": {
                        "start": format_into_utc_date(collective_offer_template.start),
                        "end": format_into_utc_date(collective_offer_template.end),
                    },
                    "formats": [fmt.value for fmt in collective_offer_template.formats],
                    "isTemplate": True,
                }
            ],
        }

    def test_location_address_venue(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        venue = offerers_factories.VenueFactory()
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            locationType=models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddress.id,
            interventionArea=None,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[collective_offer_template],
        )

        test_client = get_test_client(client, educational_redactor, educational_institution)
        with assert_num_queries(self.num_queries):
            response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        [result] = response.json["favoritesTemplate"]
        response_location = result["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is True
        assert response_location["location"]["banId"] == venue.offererAddress.address.banId

    def test_missing_institution_id(self, client):
        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = get_test_client(client, educational_redactor, None)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 403
        assert "institution" in response.json["message"]
