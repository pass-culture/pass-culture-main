from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.public.united.endpoints.collective_offers import create_collective_offer

from tests.routes import image_data
from tests.routes.public.united import helpers


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="institution")
def institution_fixture():
    return educational_factories.EducationalInstitutionFactory()


@pytest.fixture(name="national_program")
def national_program_fixture():
    return educational_factories.NationalProgramFactory()


@pytest.fixture(name="domain")
def domain_fixture(national_program):
    return educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])


@pytest.fixture(name="payload")
def payload_fixture(domain, institution, national_program, venue):
    return {
        "venueId": venue.id,
        "name": "Un nom en français ævœc des diàcrtîtïqués",
        "description": "une description d'offre",
        "formats": [subcategories.EacFormat.CONCERT.value],
        "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
        "contactEmail": "offerer-contact@example.com",
        "contactPhone": "+33100992798",
        "domains": [domain.id],
        "durationMinutes": 183,
        "students": [models.StudentLevels.COLLEGE4.name],
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": True,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
        "offerVenue": {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        },
        "isActive": True,
        "nationalProgramId": national_program.id,
        # stock part
        "beginningDatetime": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "bookingLimitDatetime": (datetime.utcnow() + timedelta(days=25)).isoformat(),
        "totalPrice": 35621,
        "numberOfTickets": 30,
        "educationalPriceDetail": "Justification du prix",
        # link to educational institution
        "educationalInstitutionId": institution.id,
        "imageCredit": "pouet",
        "imageFile": image_data.GOOD_IMAGE,
    }


class CreateCollectiveOfferTest(helpers.PublicApiBaseTest):
    controller = create_collective_offer

    def test_create_collective_offer(self, api_client, payload):
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            with self.assert_valid_response(api_client, payload=payload) as response:
                assert response["name"] == payload["name"]
                assert response["isActive"]
                assert response["status"] == OfferStatus.ACTIVE.value
                assert not response["bookings"]
                assert not response["isSoldOut"]

                offer = models.CollectiveOffer.query.first()
                assert offer is not None
                assert offer.name == payload["name"]
                assert offer.isActive
                assert offer.status == OfferStatus.ACTIVE
                assert not offer.isSoldOut

                stock = offer.collectiveStock
                assert stock is not None
                assert stock.numberOfTickets == payload["numberOfTickets"]
                assert not stock.collectiveBookings

    class UnauthorizedTest(helpers.UnauthorizedBaseTest):
        controller = create_collective_offer

        def test_cultural_partner_not_found(self, api_client, payload):
            side_effect = [exceptions.CulturalPartnerNotFoundException]
            assert_no_collective_offer_created(self, api_client, payload, side_effect)

        def test_educational_institution_is_not_active(self, api_client, payload, institution):
            institution.isActive = False
            assert_no_collective_offer_created(self, api_client, payload)

    class NotFoundTest(helpers.NotFoundBaseTest):
        controller = create_collective_offer

        def test_unknown_venue(self, api_client, payload):
            payload["venueId"] = -1
            assert "venueId" in self.assert_is_not_known(api_client, payload)

        def test_not_my_venue(self, api_client, payload, unrelated_venue):
            payload["venueId"] = unrelated_venue.id
            assert "venueId" in self.assert_is_not_known(api_client, payload)

        def test_unknown_institution(self, api_client, payload):
            payload["educationalInstitutionId"] = -1
            assert "educationalInstitutionId" in self.assert_is_not_known(api_client, payload)

        def assert_is_not_known(self, api_client, payload, side_effect=None):
            return assert_no_collective_offer_created(self, api_client, payload, side_effect)

    class BadRquestTest(helpers.BadRequestBaseTest):
        controller = create_collective_offer

        def test_unknown_domains(self, api_client, payload):
            payload["domains"] = [-1]

            with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
                with self.assert_valid_response(api_client, payload=payload) as response:
                    assert models.CollectiveOffer.query.count() == 0
                    assert "domains" in response


def assert_no_collective_offer_created(test_instance, api_client, payload, side_effect=None):
    mock_path = "pcapi.core.offerers.api.can_offerer_create_educational_offer"
    with patch(mock_path) as mock:
        mock.side_effect = side_effect

        with test_instance.assert_valid_response(api_client, payload=payload) as response:
            assert models.CollectiveOffer.query.count() == 0
            return response


class CreateCollectiveOfferUnauthenticatedTest(helpers.PublicApiBaseTest, helpers.UnauthenticatedMixin):
    controller = create_collective_offer
