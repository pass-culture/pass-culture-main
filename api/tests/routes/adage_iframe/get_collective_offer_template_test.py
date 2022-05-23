from datetime import datetime
from typing import ByteString

from freezegun.api import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.testing import assert_num_queries

from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


def _create_adage_valid_token_with_email(
    email: str,
    civility: str = "Mme",
    lastname: str = "LAPROF",
    firstname: str = "Jeanne",
    uai: str = "EAU123",
) -> ByteString:
    return create_adage_jwt_fake_valid_token(
        civility=civility, lastname=lastname, firstname=firstname, email=email, uai=uai
    )


@freeze_time("2020-11-17 15:00:00")
class Returns200Test:
    def test_get_collective_offer_template(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory(
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
        )
        offer_id = offer.id

        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        with assert_num_queries(1):
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
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "offerVenue": offer.offerVenue,
            "students": ["Lycée - Seconde"],
            "offerId": None,
            "educationalPriceDetail": "détail du prix",
            "domains": [{"id": offer.domains[0].id, "name": offer.domains[0].name}],
        }


class Returns404Test:
    def test_should_return_404_when_no_collective_offer_template(self, client):
        # Given
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get("/adage-iframe/collective/offers-template/0")

        # Then
        assert response.status_code == 404
