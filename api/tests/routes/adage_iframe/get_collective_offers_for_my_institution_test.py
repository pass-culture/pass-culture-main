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
    # 1. fetch redactor
    # 2. fetch collective offer and related data
    # 3. fetch feature toggle
    # 4. fetch the offerVenue's details (Venue)
    num_queries = 4

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_get_collective_offer_for_my_institution_without_feature_toggle(self, eac_client, redactor):
        START_DATE = datetime.today() + timedelta(days=3)
        venue = offerers_factories.VenueFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId=UAI)
        stocks = educational_factories.CollectiveStockFactory.create_batch(
            3,
            startDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        # this archived offer should not appear in the result
        stocks[2].collectiveOffer.dateArchived = datetime.utcnow() - timedelta(days=1)
        stocks[2].collectiveOffer.isActive = False

        # cancelled booking should appear in the result when the feature toggle is disabled
        stock_with_cancelled_booking = educational_factories.CollectiveStockFactory(
            startDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=stock_with_cancelled_booking)

        dst = url_for("adage_iframe.get_collective_offers_for_my_institution")

        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
        response_data = sorted(response.json["collectiveOffers"], key=lambda offer: offer["id"])
        assert len(response_data) == 3, response_data
        assert response_data[0]["id"] == stocks[0].collectiveOffer.id
        assert response_data[0]["educationalInstitution"]["id"] == institution.id
        assert response_data[0]["stock"]["id"] == stocks[0].id
        assert response_data[1]["id"] == stocks[1].collectiveOffer.id
        assert response_data[1]["educationalInstitution"]["id"] == institution.id
        assert response_data[1]["stock"]["id"] == stocks[1].id
        assert response_data[2]["id"] == stock_with_cancelled_booking.collectiveOffer.id

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_get_collective_offer_for_my_institution_with_feature_toggle(self, eac_client, redactor):
        START_DATE = datetime.today() + timedelta(days=3)
        venue = offerers_factories.VenueFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId=UAI)
        stocks = educational_factories.CollectiveStockFactory.create_batch(
            3,
            startDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        # this archived offer should not appear in the result
        stocks[2].collectiveOffer.dateArchived = datetime.utcnow() - timedelta(days=1)
        stocks[2].collectiveOffer.isActive = False

        # cancelled booking should not appear in the result when the feature toggle is enabled
        stock_with_cancelled_booking = educational_factories.CollectiveStockFactory(
            startDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=stock_with_cancelled_booking)

        dst = url_for("adage_iframe.get_collective_offers_for_my_institution")

        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
        response_data = sorted(response.json["collectiveOffers"], key=lambda offer: offer["id"])
        assert len(response_data) == 2, response_data
        assert response_data[0]["id"] == stocks[0].collectiveOffer.id
        assert response_data[0]["educationalInstitution"]["id"] == institution.id
        assert response_data[0]["stock"]["id"] == stocks[0].id
        assert response_data[1]["id"] == stocks[1].collectiveOffer.id
        assert response_data[1]["educationalInstitution"]["id"] == institution.id
        assert response_data[1]["stock"]["id"] == stocks[1].id
