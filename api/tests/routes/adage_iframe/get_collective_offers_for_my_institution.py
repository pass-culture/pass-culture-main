from datetime import datetime
from datetime import timedelta

from flask import url_for
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


UAI = "1234UAI"
EMAIL = "toto@mail.com"


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai=UAI)


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory(email=EMAIL)


class CollectiveOfferTest:
    def test_get_collective_offer_for_my_institution(self, eac_client, redactor):
        # Given
        START_DATE = datetime.today() + timedelta(days=3)
        venue = offerers_factories.VenueFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId=UAI)
        stocks = educational_factories.CollectiveStockFactory.create_batch(
            2,
            beginningDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )

        dst = url_for("adage_iframe.get_collective_offers_for_my_institution")

        # When
        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        with assert_num_queries(4):
            response = eac_client.get(dst)

            # Then
            assert response.status_code == 200
            response_data = sorted(response.json["collectiveOffers"], key=lambda offer: offer["id"])
            assert len(response_data) == 2, response_data
            assert response_data[0]["id"] == stocks[0].collectiveOffer.id
            assert response_data[0]["educationalInstitution"]["id"] == institution.id
            assert response_data[0]["stock"]["id"] == stocks[0].id
            assert response_data[1]["id"] == stocks[1].collectiveOffer.id
            assert response_data[1]["educationalInstitution"]["id"] == institution.id
            assert response_data[1]["stock"]["id"] == stocks[1].id
