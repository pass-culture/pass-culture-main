from datetime import datetime

from freezegun.api import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.models import offer_mixin

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


@freeze_time("2020-11-17 15:00:00")
class CollectiveOfferTest:
    def test_get_collective_offer(self, client):
        # Given
        institution = educational_factories.EducationalInstitutionFactory(institutionId="12890AI")
        national_program = educational_factories.NationalProgramFactory()
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            offer__name="offer name",
            offer__description="offer description",
            price=10,
            offer__students=[StudentLevels.GENERAL2],
            offer__educational_domains=[educational_factories.EducationalDomainFactory()],
            offer__institution=institution,
            offer__teacher=educational_factories.EducationalRedactorFactory(),
            offer__nationalProgramId=national_program.id,
        )

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email="toto@mail.com",
            uai=institution.institutionId,
        )
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}
        offer_id = stock.offer.id

        # When
        with assert_no_duplicated_queries():
            response = client.get(f"/adage-iframe/collective/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer_id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "stock": {
                "beginningDatetime": "2021-05-15T00:00:00Z",
                "bookingLimitDatetime": "2021-05-14T23:00:00Z",
                "id": stock.id,
                "isBookable": True,
                "price": 1000,
                "educationalPriceDetail": stock.priceDetail,
                "numberOfTickets": stock.numberOfTickets,
            },
            "subcategoryLabel": stock.offer.subcategory.app_label,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "id": stock.offer.venue.id,
                "name": stock.offer.venue.name,
                "postalCode": "75000",
                "publicName": stock.offer.venue.publicName,
                "managingOfferer": {"name": stock.offer.venue.managingOfferer.name},
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": stock.offer.contactEmail,
            "contactPhone": stock.offer.contactPhone,
            "offerVenue": {
                "addressType": "other",
                "address": None,
                "city": None,
                "name": None,
                "otherAddress": stock.offer.offerVenue["otherAddress"],
                "postalCode": None,
                "publicName": None,
                "venueId": stock.offer.offerVenue["venueId"],
            },
            "students": ["Lycée - Seconde"],
            "offerId": None,
            "educationalPriceDetail": stock.priceDetail,
            "domains": [{"id": stock.offer.domains[0].id, "name": stock.offer.domains[0].name}],
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
                "email": stock.offer.teacher.email,
                "firstName": stock.offer.teacher.firstName,
                "lastName": stock.offer.teacher.lastName,
                "civility": stock.offer.teacher.civility,
            },
            "nationalProgram": {"id": national_program.id, "name": national_program.name},
        }

    def test_get_collective_offer_with_offer_venue(self, client):
        # Given
        institution = educational_factories.EducationalInstitutionFactory(institutionId="pouet")
        venue = offerers_factories.VenueFactory()
        national_program = educational_factories.NationalProgramFactory()
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            offer__name="offer name",
            offer__description="offer description",
            price=10,
            offer__students=[StudentLevels.GENERAL2],
            offer__educational_domains=[educational_factories.EducationalDomainFactory()],
            offer__institution=institution,
            offer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            offer__nationalProgramId=national_program.id,
        )

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email="toto@mail.com",
            uai="autre",
        )
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}
        offer_id = stock.offer.id

        # When
        with assert_no_duplicated_queries():
            response = client.get(f"/adage-iframe/collective/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer_id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "stock": {
                "beginningDatetime": "2021-05-15T00:00:00Z",
                "bookingLimitDatetime": "2021-05-14T23:00:00Z",
                "id": stock.id,
                "isBookable": True,
                "price": 1000,
                "educationalPriceDetail": stock.priceDetail,
                "numberOfTickets": stock.numberOfTickets,
            },
            "subcategoryLabel": stock.offer.subcategory.app_label,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "id": stock.offer.venue.id,
                "name": stock.offer.venue.name,
                "postalCode": "75000",
                "publicName": stock.offer.venue.publicName,
                "managingOfferer": {"name": stock.offer.venue.managingOfferer.name},
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": stock.offer.contactEmail,
            "contactPhone": stock.offer.contactPhone,
            "offerVenue": {
                "addressType": "offererVenue",
                "address": venue.address,
                "city": venue.city,
                "name": venue.name,
                "otherAddress": "",
                "postalCode": venue.postalCode,
                "publicName": venue.publicName,
                "venueId": venue.id,
            },
            "students": ["Lycée - Seconde"],
            "offerId": None,
            "educationalPriceDetail": stock.priceDetail,
            "domains": [{"id": stock.offer.domains[0].id, "name": stock.offer.domains[0].name}],
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
            "teacher": None,
            "nationalProgram": {"id": national_program.id, "name": national_program.name},
        }

    def test_should_return_404_when_no_collective_offer(self, client):
        # Given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get("/adage-iframe/collective/offers/0")

        # Then
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation",
        [
            offer_mixin.OfferValidationStatus.DRAFT,
            offer_mixin.OfferValidationStatus.PENDING,
            offer_mixin.OfferValidationStatus.REJECTED,
        ],
    )
    def test_should_return_404_when_collective_offer_template_is_not_approved(self, client, validation):
        # Given
        offer = educational_factories.CollectiveOfferFactory(validation=validation)

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get(f"/adage-iframe/collective/offers/{offer.id}")

        # Then
        assert response.status_code == 404
