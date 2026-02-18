from datetime import datetime

import pytest
import time_machine
from flask import url_for

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import offer_mixin


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


EMAIL = "toto@mail.com"


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai="1234UAI")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory(email=EMAIL)


class CollectiveOfferTest:
    num_queries = 1  # fetch collective offer and related data
    num_queries += 1  # fetch redactor

    @time_machine.travel("2020-11-17 15:00:00")
    def test_get_collective_offer(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="12890AI")
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 5, 15),
            collectiveOffer__name="offer name",
            collectiveOffer__description="offer description",
            price=10,
            collectiveOffer__students=[models.StudentLevels.GENERAL2],
            collectiveOffer__educational_domains=[educational_factories.EducationalDomainFactory()],
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(),
            collectiveOffer__nationalProgramId=educational_factories.NationalProgramFactory().id,
            collectiveOffer__venue=venue,
            collectiveOffer__locationType=models.CollectiveLocationType.ADDRESS,
            collectiveOffer__offererAddress=venue.offererAddress,
        )
        offer = stock.collectiveOffer

        dst = url_for("adage_iframe.get_collective_offer", offer_id=stock.collectiveOfferId)
        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        oa = offer.offererAddress
        address = oa.address

        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer.id,
            "name": "offer name",
            "stock": {
                "startDatetime": "2021-05-15T00:00:00Z",
                "endDatetime": "2021-05-15T00:00:00Z",
                "bookingLimitDatetime": "2021-05-14T23:00:00Z",
                "id": stock.id,
                "price": 1000,
                "educationalPriceDetail": stock.priceDetail,
                "numberOfTickets": stock.numberOfTickets,
            },
            "venue": {
                "adageId": None,
                "address": venue.offererAddress.address.street,
                "city": venue.offererAddress.address.city,
                "coordinates": {
                    "latitude": float(venue.offererAddress.address.latitude),
                    "longitude": float(venue.offererAddress.address.longitude),
                },
                "id": offer.venue.id,
                "imgUrl": None,
                "managingOfferer": {"name": offer.venue.managingOfferer.name},
                "name": offer.venue.name,
                "postalCode": venue.offererAddress.address.postalCode,
                "departmentCode": venue.offererAddress.address.departmentCode,
                "publicName": offer.venue.publicName,
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "location": {
                "locationType": offer.locationType.value,
                "locationComment": offer.locationComment,
                "location": {
                    "banId": address.banId,
                    "city": address.city,
                    "departmentCode": address.departmentCode,
                    "id": address.id,
                    "inseeCode": address.inseeCode,
                    "isManualEdition": address.isManualEdition,
                    "label": venue.common_name,
                    "latitude": float(address.latitude),
                    "longitude": float(address.longitude),
                    "postalCode": address.postalCode,
                    "street": address.street,
                    "isVenueLocation": True,
                },
            },
            "students": ["Lycée - Seconde"],
            "educationalPriceDetail": stock.priceDetail,
            "domains": [{"id": offer.domains[0].id, "name": offer.domains[0].name}],
            "educationalInstitution": {
                "id": institution.id,
                "institutionType": institution.institutionType,
                "name": institution.name,
                "city": institution.city,
                "postalCode": institution.postalCode,
            },
            "interventionArea": ["93", "94", "95"],
            "imageUrl": None,
            "teacher": {
                "email": offer.teacher.email,
                "firstName": offer.teacher.firstName,
                "lastName": offer.teacher.lastName,
                "civility": offer.teacher.civility,
            },
            "nationalProgram": {"id": offer.nationalProgramId, "name": offer.nationalProgram.name},
            "formats": [fmt.value for fmt in offer.formats],
            "isTemplate": False,
        }

    def test_location_address_venue(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue,
            locationType=models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddress.id,
            interventionArea=None,
        )

        dst = url_for("adage_iframe.get_collective_offer", offer_id=offer.id)
        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
        response_location = response.json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is True
        assert response_location["location"]["banId"] == venue.offererAddress.address.banId

    def test_should_return_404_when_no_collective_offer(self, eac_client, redactor):
        response = eac_client.get("/adage-iframe/collective/offers/0")
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation",
        [
            offer_mixin.OfferValidationStatus.DRAFT,
            offer_mixin.OfferValidationStatus.PENDING,
            offer_mixin.OfferValidationStatus.REJECTED,
        ],
    )
    def test_should_return_404_when_collective_offer_template_is_not_approved(self, eac_client, redactor, validation):
        offer = educational_factories.CollectiveOfferTemplateFactory(validation=validation)
        response = eac_client.get(f"/adage-iframe/collective/offers/{offer.id}")
        assert response.status_code == 404

    def test_non_redactor_is_ok(self, eac_client):
        """Ensure that an authenticated user that is a not an
        educational redactor can still fetch offers informations.
        """
        offer = educational_factories.CollectiveStockFactory().collectiveOffer
        dst = url_for("adage_iframe.get_collective_offer", offer_id=offer.id)

        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
