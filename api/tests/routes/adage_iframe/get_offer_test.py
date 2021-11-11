from datetime import datetime
from typing import ByteString
from typing import Optional

from freezegun.api import freeze_time
import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.testing import assert_num_queries

from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


def _create_adage_valid_token_with_email(
    email: str,
    civility: Optional[str] = "Mme",
    lastname: Optional[str] = "LAPROF",
    firstname: Optional[str] = "Jeanne",
    uai: Optional[str] = "EAU123",
) -> ByteString:
    return create_adage_jwt_fake_valid_token(
        civility=civility, lastname=lastname, firstname=firstname, email=email, uai=uai
    )


@freeze_time("2020-11-17 15:00:00")
class Returns200Test:
    def test_get_offer(self, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory(name="offer name", description="offer description")
        stock1 = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            offer=offer,
        )
        stock2 = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 5, 16),
            offer=offer,
            price=200,
        )

        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}
        offer_id = offer.id

        # When
        with assert_num_queries(1):
            response = client.get(f"/adage-iframe/offer/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer_id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "stocks": [
                {
                    "beginningDatetime": "2021-05-15T00:00:00Z",
                    "id": stock1.id,
                    "isBookable": True,
                    "price": 1000,
                },
                {
                    "beginningDatetime": "2021-05-16T00:00:00Z",
                    "id": stock2.id,
                    "isBookable": True,
                    "price": 20000,
                },
            ],
            "subcategoryLabel": "Séance de cinéma",
            "venue": {
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "id": offer.venue.id,
                "name": offer.venue.name,
                "postalCode": "75000",
                "publicName": offer.venue.publicName,
            },
        }


class Returns404Test:
    def test_should_return_404_when_no_offer(self, client):
        # Given
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get("/adage-iframe/offer/1000")

        # Then
        assert response.status_code == 404
