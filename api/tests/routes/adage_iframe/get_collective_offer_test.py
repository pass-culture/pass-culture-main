from datetime import datetime

from flask import url_for
import pytest
import time_machine

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
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
    @time_machine.travel("2020-11-17 15:00:00")
    def test_get_collective_offer(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="12890AI")
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 5, 15),
            endDatetime=datetime(2021, 5, 15),
            collectiveOffer__subcategoryId=subcategories.SEANCE_CINE.id,
            collectiveOffer__name="offer name",
            collectiveOffer__description="offer description",
            price=10,
            collectiveOffer__students=[StudentLevels.GENERAL2],
            collectiveOffer__educational_domains=[educational_factories.EducationalDomainFactory()],
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(),
            collectiveOffer__nationalProgramId=educational_factories.NationalProgramFactory().id,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        offer = stock.collectiveOffer

        dst = url_for("adage_iframe.get_collective_offer", offer_id=stock.collectiveOfferId)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        # 5. fetch the venue's images
        with assert_num_queries(5):
            response = eac_client.get(dst)

        # Then
        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer.id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "stock": {
                "startDatetime": "2021-05-15T00:00:00Z",
                "endDatetime": "2021-05-15T00:00:00Z",
                "bookingLimitDatetime": "2021-05-14T23:00:00Z",
                "id": stock.id,
                "isBookable": True,
                "price": 1000,
                "educationalPriceDetail": stock.priceDetail,
                "numberOfTickets": stock.numberOfTickets,
            },
            "venue": {
                "adageId": None,
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "distance": None,
                "id": offer.venue.id,
                "imgUrl": None,
                "managingOfferer": {"name": offer.venue.managingOfferer.name},
                "name": offer.venue.name,
                "postalCode": "75000",
                "departmentCode": offer.venue.departementCode,
                "publicName": offer.venue.publicName,
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "offerVenue": {
                "addressType": "offererVenue",
                "address": venue.street,
                "city": venue.city,
                "distance": None,
                "name": venue.name,
                "otherAddress": "",
                "postalCode": venue.postalCode,
                "publicName": venue.publicName,
                "venueId": venue.id,
            },
            "students": ["Lycée - Seconde"],
            "offerId": None,
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
            "imageCredit": None,
            "imageUrl": None,
            "teacher": {
                "email": offer.teacher.email,
                "firstName": offer.teacher.firstName,
                "lastName": offer.teacher.lastName,
                "civility": offer.teacher.civility,
            },
            "nationalProgram": {"id": offer.nationalProgramId, "name": offer.nationalProgram.name},
            "isFavorite": False,
            "formats": [fmt.value for fmt in subcategories.SEANCE_CINE.formats],
            "isTemplate": False,
        }

    def test_is_a_redactors_favorite(self, eac_client):
        """Ensure that the isFavorite field is true only if the
        redactor added it to its favorites.
        """
        offer = educational_factories.CollectiveStockFactory().collectiveOffer
        educational_factories.EducationalRedactorFactory(email=EMAIL, favoriteCollectiveOffers=[offer])

        dst = url_for("adage_iframe.get_collective_offer", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. find out if its a redactor's favorite
        # 4. fetch the venue's images
        with assert_num_queries(4):
            response = eac_client.get(dst)

        # Then
        assert response.status_code == 200
        assert response.json["isFavorite"]

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

    def test_offer_venue_has_an_empty_string_venue_id(self, client):
        # TODO(jeremieb): remove this test once there is no empty
        # string stored as a venueId
        redactor = educational_factories.EducationalRedactorFactory()
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__offerVenue={"venueId": "", "addressType": "other", "otherAddress": "REDACTED"}
        )

        eac_client = client.with_adage_token(email=redactor.email, uai="1234UAI")
        response = eac_client.get(f"/adage-iframe/collective/offers/{stock.collectiveOfferId}")
        assert response.status_code == 200

    def test_non_redactor_is_ok(self, eac_client):
        """Ensure that an authenticated user that is a not an
        educational redactor can still fetch offers informations.
        """
        offer = educational_factories.CollectiveStockFactory().collectiveOffer
        dst = url_for("adage_iframe.get_collective_offer", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the venue's images
        with assert_num_queries(3):
            response = eac_client.get(dst)

        assert response.status_code == 200
