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
class CollectiveOfferTemplateTest:
    def test_get_collective_offer_template(self, client):
        # Given
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            nationalProgramId=national_program.id,
        )
        offer_id = offer.id

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        with assert_no_duplicated_queries():
            response = client.get(f"/adage-iframe/collective/offers-template/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer.id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "subcategoryLabel": offer.subcategory.app_label,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "id": offer.venue.id,
                "name": offer.venue.name,
                "postalCode": "75000",
                "publicName": offer.venue.publicName,
                "managingOfferer": {"name": offer.venue.managingOfferer.name},
            },
            "interventionArea": offer.interventionArea,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "offerVenue": {
                "addressType": "other",
                "address": None,
                "city": None,
                "name": None,
                "otherAddress": offer.offerVenue["otherAddress"],
                "postalCode": None,
                "publicName": None,
                "venueId": offer.offerVenue["venueId"],
            },
            "students": ["Lycée - Seconde"],
            "offerId": None,
            "educationalPriceDetail": "détail du prix",
            "domains": [{"id": offer.domains[0].id, "name": offer.domains[0].name}],
            "imageUrl": None,
            "imageCredit": None,
            "nationalProgramId": national_program.id,
        }

    def test_get_collective_offer_template_with_offer_venue(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=national_program.id,
        )
        offer_id = offer.id

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        with assert_no_duplicated_queries():
            response = client.get(f"/adage-iframe/collective/offers-template/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer.id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "subcategoryLabel": offer.subcategory.app_label,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "id": offer.venue.id,
                "name": offer.venue.name,
                "postalCode": "75000",
                "publicName": offer.venue.publicName,
                "managingOfferer": {"name": offer.venue.managingOfferer.name},
            },
            "interventionArea": offer.interventionArea,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
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
            "educationalPriceDetail": "détail du prix",
            "domains": [{"id": offer.domains[0].id, "name": offer.domains[0].name}],
            "imageUrl": None,
            "imageCredit": None,
            "nationalProgramId": national_program.id,
        }

    def test_should_return_404_when_no_collective_offer_template(self, client):
        # Given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get("/adage-iframe/collective/offers-template/0")

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
        offer = educational_factories.CollectiveOfferTemplateFactory(validation=validation)

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get(f"/adage-iframe/collective/offers-template/{offer.id}")

        # Then
        assert response.status_code == 404
